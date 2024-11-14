import json
from pathlib import Path
from threading import Thread, Event

import cv2
import pandas as pd
import mediapipe as mp
from flatbuffers.builder import np

from kls_mcmarr.kls.capture.global_values import GlobalValues
from kls_mcmarr.kls.capture.mediapipe_wrapper.utils import get_list_landmarks_sorted
from kls_mcmarr.kls.capture.mediapipe_wrapper.mediapipe_anonymize_image import AnonymizeWithMediapipe


class RecordWithMediapipe(Thread):

    def __init__(self, capture_mode="video", input_video_path=None, camera_num=0, output_path="assets/output/capture/",
                 show_output=False, formats_to_store=None, autofocus=1, max_frames_to_capture=100):
        super().__init__()

        # Anonymization
        self.anonymize = AnonymizeWithMediapipe()

        # MediaPipe vars
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_pose = mp.solutions.pose

        # Output information.
        if formats_to_store is None:
            self.formats_to_store = []
        else:
            self.formats_to_store = formats_to_store
        self.json_captured_data = {}
        self.list_captured_data = []
        self.mediapipe_results = []
        self.csv_captured_data = ""
        self.initialize_csv_with_header()

        # Capture mode ("camera" or "video").
        self.capture_mode = capture_mode

        # Webcam information.
        self.capture_device = None
        self.camera_num = camera_num
        self.autofocus = autofocus

        # Webcam control.
        self.stop_capture = False

        # Video information.
        self.input_video_path = input_video_path
        self.output_path = output_path
        if not self.output_path.endswith("/"):
            self.output_path = self.output_path + "/"

        # Video output
        self.raw_captured_video = None
        self.processed_captured_video = None
        self.processed_captured_video_skeleton_only = None
        self.show_output = show_output
        self.uuid_name = None

        # Frame counter
        self.num_frames = 0
        self.frame_limit = max_frames_to_capture
        self.frame_limit_reached = Event()

        # Create output path if not exist.
        Path(self.output_path).mkdir(parents=True, exist_ok=True)

    def run(self):
        """
        Start the capture of the movements using the camera selected when creating this object.
        :return: None.
        """

        # Print available camera APIs.
        # print("Available Camera APIs:")
        # available_backends = [cv2.videoio_registry.getBackendName(b) for b in cv2.videoio_registry.getBackends()]
        # print(available_backends)

        # Select capture mode.
        fps = 0
        if self.capture_mode == "camera" and self.capture_device is None:
            self.capture_device = cv2.VideoCapture(self.camera_num, cv2.CAP_DSHOW)
            self.capture_device.set(cv2.CAP_PROP_AUTOFOCUS, self.autofocus)
            fps = 15
        elif self.capture_mode == "video" and self.capture_device is None:
            self.capture_device = cv2.VideoCapture(self.input_video_path)
            fps = int(self.capture_device.get(cv2.CAP_PROP_FPS))

        # Update fps GlobalValues.
        GlobalValues.fps = fps

        # Get width and height of camera captured images.
        frame_width = int(self.capture_device.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.capture_device.get(cv2.CAP_PROP_FRAME_HEIGHT))
        size = (frame_width, frame_height)

        GlobalValues.frame_width = frame_width
        GlobalValues.frame_height = frame_height

        # Create a video writer to write all the frames here.
        self.raw_captured_video = cv2.VideoWriter(self.output_path + self.uuid_name + "_raw.webm",
                                                  cv2.VideoWriter_fourcc(*'vp80'), fps, size)
        self.processed_captured_video = cv2.VideoWriter(self.output_path + self.uuid_name + "_processed.webm",
                                                        cv2.VideoWriter_fourcc(*'vp80'), fps, size)
        self.processed_captured_video_skeleton_only = cv2.VideoWriter(
            self.output_path + self.uuid_name + "_processed_skeleton.webm", cv2.VideoWriter_fourcc(*'vp80'), fps, size)

        # We don't want to stop camera.
        self.stop_capture = False
        self.capture()

    def stop(self):
        """
        Stop the capture of the movements.
        :return: None
        """
        # Send signal to thread so it stops capturing.
        self.stop_capture = True

        # Join thread.
        self.join()

        # Release the webcam.
        self.capture_device.release()
        # print("Releasing camera.")

    def capture(self):
        # Clean up data from previous capture.
        self.json_captured_data = {}
        self.list_captured_data = []
        self.csv_captured_data = ""

        self.mediapipe_results = []

        # Current detected frame.
        frame_number = 1

        # Anonymized image
        # anonymized = None

        # Establish detection and parameters
        # model_complexity: https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/#models
        with self.mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7, model_complexity=2) as pose:

            # While the webcam is opened...
            while self.capture_device.isOpened() and not self.stop_capture:
                # capture an image.
                success, image = self.capture_device.read()

                # If not success reading a new image, ignore if webcam, or break if video.
                if not success:
                    # If a frame was not read, ignore if camera mode, and break if video mode.
                    if self.capture_mode == "camera":
                        # print("Ignoring empty camera frame.")
                        self.stopCam = True
                        continue
                    elif self.capture_mode == "video":
                        # print("Error loading frame.")
                        break
                    else:
                        raise NameError("Mode " + self.capture_mode + " is not a valid capture mode. Valid modes are: "
                                                                      "['camera', 'video']")
                else:
                    # Anonymize
                    # anonymized = self.anonymize.process_image(image)

                    if image is not None:
                        # Write frame in raw video.
                        self.raw_captured_video.write(image)

                        # To improve performance, optionally mark the image as not writeable to pass by reference.
                        image.flags.writeable = False
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                        # Process the image using MediaPipe
                        mediapipe_result = pose.process(image)

                        # If a pose has been detected...
                        if mediapipe_result.pose_landmarks is not None:

                            # store as json.
                            if "json" in self.formats_to_store:
                                self.store_frame_in_json(mediapipe_result, frame_number)

                            # store as csv.
                            if "csv" in self.formats_to_store:
                                self.store_frame_in_csv(mediapipe_result)

                            # Store as list.
                            self.store_frame_in_list(mediapipe_result)

                            # Store raw.
                            self.mediapipe_results.append(mediapipe_result)

                            frame_number += 1

                        # Draw the pose annotation on the image.
                        image.flags.writeable = True
                        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                        self.mp_drawing.draw_landmarks(
                            image,
                            mediapipe_result.pose_landmarks,
                            self.mp_pose.POSE_CONNECTIONS,
                            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())

                        # Create a blank white image so we can have the skeleton isolated (same size as the input image)
                        image_empty = np.ones_like(image) * 255
                        image_empty = cv2.cvtColor(image_empty, cv2.COLOR_RGB2BGR)
                        self.mp_drawing.draw_landmarks(
                            image_empty,
                            mediapipe_result.pose_landmarks,
                            self.mp_pose.POSE_CONNECTIONS,
                            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                        )

                        if self.show_output:
                            # Flip the image horizontally for a selfie-view display.
                            cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))

                        # Write frame in processed videos.
                        self.processed_captured_video.write(image)
                        self.processed_captured_video_skeleton_only.write(image_empty)

                        # Recording and process finishes when 'esc' is pressed.
                        if cv2.waitKey(5) & 0xFF == 27:
                            break

                self.num_frames += 1
                if self.num_frames == self.frame_limit:
                    self.frame_limit_reached.set()

            # Export json.
            if "json" in self.formats_to_store:
                with open(self.output_path + self.uuid_name + ".json", 'w') as f:
                    json.dump(self.json_captured_data, f, indent=4)

            # Export csv.
            if "csv" in self.formats_to_store:
                with open(self.output_path + self.uuid_name + ".csv", 'w') as f:
                    f.write(self.csv_captured_data)

            self.processed_captured_video.release()
            self.processed_captured_video_skeleton_only.release()
            self.raw_captured_video.release()

    def get_captured_data_as_list(self):
        return self.list_captured_data

    def get_captured_data_as_dataframe(self):
        # Get names of landmarks.
        landmark_strings = get_list_landmarks_sorted().keys()

        # Create header names for each landmark measure.
        header = []
        for string in landmark_strings:
            header.append(string + "_x")
            header.append(string + "_y")
            header.append(string + "_z")
            header.append(string + "_v")

        # Convert results into a pandas dataframe.
        dataframe_results = pd.DataFrame(columns=header)

        # Save each frame of mediapipe results in the dataframe.
        num_frame = 0
        for frame in self.mediapipe_results:
            if frame.pose_landmarks is None:
                dataframe_results.loc[len(dataframe_results)] = 0.0
            else:
                row = []
                for landmark in frame.pose_landmarks.landmark:
                    row.append(landmark.x)
                    row.append(landmark.y)
                    row.append(landmark.z)
                    row.append(landmark.visibility)
                dataframe_results.loc[len(dataframe_results)] = row
            num_frame += 1

        return dataframe_results

    def store_frame_in_json(self, mediapipe_result, frame_number):
        self.json_captured_data['frame ' + str(frame_number)] = {}
        landmark_number = 0
        mediapipe_landmarks = list(get_list_landmarks_sorted().keys())
        for data_point in mediapipe_result.pose_landmarks.landmark:
            self.json_captured_data['frame ' + str(frame_number)][mediapipe_landmarks[landmark_number]] = {}
            self.json_captured_data['frame ' + str(frame_number)][mediapipe_landmarks[landmark_number]][
                'x'] = data_point.x
            self.json_captured_data['frame ' + str(frame_number)][mediapipe_landmarks[landmark_number]][
                'y'] = data_point.y
            self.json_captured_data['frame ' + str(frame_number)][mediapipe_landmarks[landmark_number]][
                'z'] = data_point.z
            self.json_captured_data['frame ' + str(frame_number)][mediapipe_landmarks[landmark_number]][
                'visibility'] = data_point.visibility
            landmark_number += 1

    def initialize_csv_with_header(self):
        header = ""
        for landmark_name in get_list_landmarks_sorted().keys():
            header = header + landmark_name + "_x;"
            header = header + landmark_name + "_y;"
            header = header + landmark_name + "_z;"
            header = header + landmark_name + "_visibility;"
        header = header[:-2]
        header = header + "\n"
        self.csv_captured_data = header

    def store_frame_in_csv(self, mediapipe_result):
        for data_point in mediapipe_result.pose_landmarks.landmark:
            self.csv_captured_data = self.csv_captured_data + str(data_point.x) + "; " + str(data_point.y) + "; " + str(
                data_point.z) + "; " + str(data_point.visibility) + "; "
        self.csv_captured_data = self.csv_captured_data[:-2]
        self.csv_captured_data = self.csv_captured_data + "\n"

    def store_frame_in_list(self, mediapipe_result):
        # Store as list (Each element is a frame and contains in position 0 the name of the landmark),
        # and in position 1 the x, y and z coordinates and the visibility.
        x = []
        y = []
        z = []
        v = []
        for data_point in mediapipe_result.pose_landmarks.landmark:
            x.append(data_point.x)
            y.append(data_point.y)
            z.append(data_point.z)
            v.append(data_point.visibility)
        frame = [x, y, z, v]
        self.list_captured_data.append(frame)

    def set_uuid_name(self, uuid_name):
        self.uuid_name = uuid_name

    def clone(self):
        return RecordWithMediapipe(self.capture_mode, self.input_video_path, self.camera_num, self.output_path,
                                   self.show_output, self.formats_to_store)