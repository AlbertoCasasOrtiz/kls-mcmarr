import os
import cv2
import math
import mediapipe as mp
import numpy as np

# Define drawing and video capture functions
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Replace with your video path
video_path = "video.mp4"

# Capture video from file
cap = cv2.VideoCapture(video_path)

# Output video
output_filename = os.path.join("", 'out.mp4')
output_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
output_video = cv2.VideoWriter(output_filename, cv2.VideoWriter_fourcc(*'MJPG'), cap.get(cv2.CAP_PROP_FPS),
                               output_size)


def capture_video():

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading video, exit if frame not read
            break

        # Process frame
        process_frame(image.copy(), output_video)

        # Exit loop if 'q' key is pressed
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
    output_video.release()
    cap.release()


def process_frame(image, output_video):
    # Convert image to RGB format
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False

    # Image dimensions
    height, width, channels = image.shape

    # Run pose landmark detection
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2, enable_segmentation=True) as pose:
        # Process the image using MediaPipe
        pose_results = pose.process(image)

        # If a pose has been detected...
        if pose_results.pose_landmarks is not None:# Extract segmentation mask
            segmentation_mask = pose_results.segmentation_mask

            threshold = 0.7  # Adjust threshold value as needed
            mask_binary = np.where(segmentation_mask > threshold, 1, 0).astype(np.uint8)

            # Create a white background
            white_background = np.ones_like(image) * 255

            # Copy the original image where the mask is 1
            foreground = cv2.bitwise_and(image, image, mask=mask_binary)
            foreground = cv2.dilate(foreground, (50, 50))

            # Copy the white background where the mask is 0
            background = cv2.bitwise_and(white_background, white_background, mask=1 - mask_binary)

            # Combine the foreground and background
            result_image = cv2.add(foreground, background)


            # Draw pose landmarks on the frame
            # mp_drawing.draw_landmarks(result_image, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Blur around nose.
            nose_in_px = [pose_results.pose_landmarks.landmark[0].x * width, pose_results.pose_landmarks.landmark[0].y * height]
            left_ear = [pose_results.pose_landmarks.landmark[8].x * width, pose_results.pose_landmarks.landmark[8].y * height]
            right_ear = [pose_results.pose_landmarks.landmark[7].x * width, pose_results.pose_landmarks.landmark[7].y * height]
            distance_ears = math.dist(left_ear, right_ear)
            # Distance eyes outside
            region = result_image[int(nose_in_px[1]-distance_ears*2):int(nose_in_px[1]+distance_ears), int(nose_in_px[0]-distance_ears):int(nose_in_px[0]+distance_ears)]
            result_image[int(nose_in_px[1]-distance_ears*2):int(nose_in_px[1]+distance_ears), int(nose_in_px[0]-distance_ears):int(nose_in_px[0]+distance_ears)] = cv2.blur(region,(12,12))

            # Convert image back to BGR format
            result_image.flags.writeable = True
            result_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)

            # Display the processed frame
            cv2.imshow('MediaPipe Pose', result_image)
            output_video.write(result_image)
            cv2.waitKey(5)


# Start video capture
capture_video()