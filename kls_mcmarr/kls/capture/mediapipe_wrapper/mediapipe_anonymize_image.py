import os
import cv2
import math
import numpy as np
import mediapipe as mp

from threading import Thread


class AnonymizeWithMediapipe(Thread):

    def __init__(self):
        super().__init__()

        # Define drawing and video capture functions
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose

    def process_image(self, image):
        # Convert image to RGB format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Image dimensions
        height, width, channels = image.shape

        # Run pose landmark detection
        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2, enable_segmentation=True) as pose:
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

                # Get face region
                nose_in_px = [pose_results.pose_landmarks.landmark[0].x * width, pose_results.pose_landmarks.landmark[0].y * height]
                left_ear = [pose_results.pose_landmarks.landmark[8].x * width, pose_results.pose_landmarks.landmark[8].y * height]
                right_ear = [pose_results.pose_landmarks.landmark[7].x * width, pose_results.pose_landmarks.landmark[7].y * height]
                distance_ears = math.dist(left_ear, right_ear)
                # Distance eyes outside
                face_region = result_image[int(nose_in_px[1] - distance_ears * 2):int(nose_in_px[1] + distance_ears), int(nose_in_px[0] - distance_ears):int(nose_in_px[0] + distance_ears)]

                # Blur face region
                result_image[int(nose_in_px[1]-distance_ears*2):int(nose_in_px[1]+distance_ears), int(nose_in_px[0]-distance_ears):int(nose_in_px[0]+distance_ears)] = cv2.blur(face_region, (12, 12))

                # Convert image back to BGR format
                result_image.flags.writeable = True
                result_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)

                return result_image

            else:
                return None
