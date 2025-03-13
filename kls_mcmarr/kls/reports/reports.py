import os
import cv2
import json
import math
import mediapipe as mp
from collections import Counter

import pandas as pd

from kls_mcmarr.kls.affective.Affective import Affective
from kls_mcmarr.kls.model.model import Model
from kls_mcmarr.mcmarr.reports.ReportsMcmarr import ReportsMcmarr as _Reports


class Reports(_Reports):

    def __init__(self):
        # Define drawing and video capture functions
        super().__init__()
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose

        # Define max scores
        self.max_score_psychomotor = 19 + 12 + 13 + 11 + 7
        self.max_score_per_movement = [19, 12, 13, 11, 7]
        self.max_score_cognitive = 5

        # Define scores
        self.score_psychomotor_final = 0
        self.score_cognitive_final = 0
        self.majority_emotion_final = ""

        # Initialize affective module.
        self.affective = Affective()

    def generate_reports(self, output_path, uuid_name, detected_errors, cognitive_answers, calculate_affective=False):
        self.detected_errors = detected_errors

        # Text Report Generation
        generated_report_string = _("psychomotor_module") + "\n"
        score_psychomotor = 0
        score_to_add = 0
        per_movement_score = []
        movement_name = None
        num_movement = -1
        repeating_because_fatal = False
        detected_medium_error = False

        for iteration in self.detected_errors:
            previous_movement_name = movement_name
            iteration_number, movement_name, errors = iteration

            if previous_movement_name != movement_name:
                repeating_because_fatal = False
                detected_medium_error = False
                num_movement += 1

            generated_report_string += _("iteration") + f": {iteration_number}\n"
            generated_report_string += f" - " + _("movement_name") + f": {movement_name}\n"

            if repeating_because_fatal and previous_movement_name == movement_name:
                score_to_add = 100/len(self.max_score_per_movement)  # Max score as a percentage
                if len(per_movement_score) <= num_movement:
                    per_movement_score.append({movement_name: score_to_add})
                else:
                    per_movement_score[num_movement] = {movement_name: score_to_add}
                continue

            if not detected_medium_error:
                score_psychomotor += score_to_add
                score_to_add = 0

            if errors:
                generated_report_string += " - " + _("errors") + ":\n"
                for error in errors:
                    priority, description = error[1], error[0]
                    generated_report_string += _("priority") + f": {priority} - {description}\n"

                    if priority == 1 and not detected_medium_error:  # Mild error
                        score_to_add += (priority * 100/len(self.max_score_per_movement)) / self.max_score_per_movement[num_movement]
                    elif priority == 2:  # Medium error
                        detected_medium_error = True
                        score_to_add = 100/len(self.max_score_per_movement) / 2  # Half max score
                    elif priority == 3:  # Fatal error
                        repeating_because_fatal = True
                        break

                    if len(per_movement_score) <= num_movement:
                        per_movement_score.append({movement_name: score_to_add})
                    else:
                        per_movement_score[num_movement] = {movement_name: score_to_add}
            else:
                generated_report_string += _("no-errors") + "\n"
                if len(per_movement_score) <= num_movement:
                    per_movement_score.append({movement_name: score_to_add})
                else:
                    per_movement_score[num_movement] = {movement_name: score_to_add}

            generated_report_string += "\n"

        # Substract 20 for each key
        total_score_sum_movements = 0
        for movement in per_movement_score:
            for key in movement:  # Each dictionary has one key
                movement[key] = 20 - movement[key]
                total_score_sum_movements += movement[key]

        # Save per_movement_score to a JSON file
        with open(output_path + os.sep + "per_movement_score.json", "w") as file:
            json.dump(per_movement_score, file)

        print("Per movement score:", per_movement_score)
        print("Per movement score sum:", total_score_sum_movements)
        # Add last score.
        score_psychomotor += score_to_add

        # Calculate as percentage.
        score_psychomotor = 100-score_psychomotor
        self.score_psychomotor_final = score_psychomotor
        generated_report_string += "Score: " + str(score_psychomotor) + "%" + "\n"
        print("Score psychomotor:", score_psychomotor)

        # Merge json file for a complete scatter plot.
        merged_json = self.merge_json_files(output_path, output_path + "FullSet.json")
        merged_dataframe = self.json_to_dataframe(merged_json, output_path)

        # Model the dataframe and generate complete scatter plot.
        model = Model(generate_plots=True, output_path=output_path)
        model.model_movement(merged_dataframe, "FullSet")

        # New section for cognitive
        generated_report_string += "\n" + _("cognitive_module") + "\n"
        score_cognitive = 0
        current_question = ""
        current_id = 1
        sorted_cognitive_answers = sorted(cognitive_answers, key=lambda x: (int(x['id']), x['correct']))
        for answer in sorted_cognitive_answers:
            correct = "Y" if bool(answer["correct"]) else "N"
            if current_question != answer["question"]:
                current_question = answer["question"]
                current_id = answer["id"]
                if not bool(answer["correct"]):
                    score_cognitive += 1
            if not bool(answer["correct"]):
                correct = "N"
            generated_report_string += f" - Question {current_id}: {answer['question']}\n"
            generated_report_string += f"     Answer: {answer['answer']} {correct}\n"
        score_cognitive = ((self.max_score_cognitive - score_cognitive) * 100) / self.max_score_cognitive
        self.score_cognitive_final = score_cognitive
        generated_report_string += "Score: " + str(score_cognitive) + "%" + "\n"

        # New section for affective
        affective_data = None
        majority_emotion = None
        if calculate_affective:
            if not self.are_videos_analyzed(output_path):
                self.analyze_videos(output_path)
            generated_report_string += "\n" + _("affective_module") + "\n"
            affective_data, majority_emotion = self.load_and_process_files(output_path)
            self.majority_emotion_final = majority_emotion

            for name, percentages in affective_data.items():
                generated_report_string += " - " + f"{name}:\n"
                for emotion, percentage in percentages.items():
                    generated_report_string += "   " + "  " + f"{emotion}: {percentage:.2f}%\n"

            generated_report_string += " - " + _("affective_main_emotion") + ": " + majority_emotion

        # Write to text file
        text_file = open(output_path + "Full Report.txt", 'w')
        text_file.write(generated_report_string)
        text_file.close()

        # HTML Report Generation
        html_report_string = f"<h1>Summary:</h1>"
        html_report_string += f"<h2>{_('affective_main_emotion')}:</strong> {majority_emotion}</h2>"
        html_report_string += f"<h2>Psychomotor Score: {score_psychomotor}%</h2>"
        html_report_string += f"<h2>Cognitive Score: {score_cognitive}%</h2>"

        # Dynamically collect media files for this iteration
        image_file = None
        json_file = None
        csv_file = None

        # Scan the output directory to identify the relevant files
        for file in os.listdir(output_path):
            if file.startswith("FullSet"):
                if file.endswith(".png"):
                    image_file = file
                if file.endswith(".json"):
                    json_file = file
                if file.endswith(".csv"):
                    csv_file = file

        if image_file:
            html_report_string += f'<img src="{image_file}" alt="Scatter Plot of full set." style="max-width:300;"/>'

        html_report_string += f'</br>'

        if json_file:
            html_report_string += f'</br><a href="{json_file}" download>Download JSON File</a>'

        html_report_string += f'</br>'

        if csv_file:
            html_report_string += f'</br><a href="{csv_file}" download>Download CSV File</a>'

        # Start full report here.
        html_report_string += f'</br>'
        html_report_string += f"<html><head><title>Full Report</title></head><body>"
        html_report_string += f"<h1>{_('psychomotor_module')}</h1>"
        html_report_string += f"<h2>Psychomotor Score: {score_psychomotor}%</h2>"

        for iteration in self.detected_errors:
            iteration_number = iteration[0]
            html_report_string += f"<h2>{_('iteration')}: {iteration_number}</h2>"
            html_report_string += f"<p><strong>{_('movement_name')}:</strong> {iteration[1]}</p>"

            if len(iteration[2]) > 0:
                html_report_string += f"<p><strong>{_('errors')}:</strong></p><ul>"
                for error in iteration[2]:
                    html_report_string += f"<li style='color: red;'>{_('priority')}: {str(error[1])} - {error[0]}</li>"
                html_report_string += "</ul>"
            else:
                html_report_string += f"<p style='color: green;'>{_('no-errors')}</p>"

            # Dynamically collect media files for this iteration
            image_file = None
            json_file = None
            csv_file = None
            video_files = []

            # Scan the output directory to identify the relevant files
            for file in os.listdir(output_path):
                if file.startswith(str(iteration_number)):
                    if file.endswith(".png"):
                        image_file = file
                    elif file.endswith(".webm"):
                        video_files.append(file)
                    elif file.endswith(".json") and not file.endswith("-affective.json"):
                        json_file = file
                    elif file.endswith(".csv"):
                        csv_file = file

            # Include collected files in the HTML report
            if image_file:
                html_report_string += f'<img src="{image_file}" alt="Iteration {iteration_number} Image" style="max-width:300;"/>'

            html_report_string += f'</br>'

            for video_file in video_files:
                html_report_string += f'<video width="300" height="225" controls><source src="{video_file}" type="video/webm">Your browser does not support the video tag.</video>'

            html_report_string += f'</br>'

            if json_file:
                html_report_string += f'</br><a href="{json_file}" download>Download JSON File</a>'

            html_report_string += f'</br>'

            if csv_file:
                html_report_string += f'</br><a href="{csv_file}" download>Download CSV File</a>'

        # Cognitive Module
        html_report_string += f"<h1>{_('cognitive_module')}</h1>"
        html_report_string += f"<h2>Cognitive Score: {score_cognitive}%</h2>"
        current_question = ""
        current_id = 1
        for answer in sorted_cognitive_answers:
            correct_symbol = "&#x2713;" if bool(answer["correct"]) else "&#x2717;"
            color = "green" if bool(answer["correct"]) else "red"
            if current_question != answer["question"]:
                current_question = answer["question"]
                current_id = answer["id"]
            html_report_string += f"<p style='color: {color};'><strong>Question {current_id}:</strong> {answer['question']}</p>"
            html_report_string += f"<p style='color: {color};'><strong> - Answer:</strong> {answer['answer']} {correct_symbol}</p>"

        # Affective Module
        if calculate_affective:
            html_report_string += f"<h1>{_('affective_module')}</h1>"
            html_report_string += f"<h2>{_('affective_main_emotion')}:</strong> {majority_emotion}</h2>"
            iteration_number = 0
            for name, percentages in affective_data.items():
                html_report_string += f"<h3>{name}</h3><ul>"
                for emotion, percentage in percentages.items():
                    html_report_string += f"<li>{emotion}: {percentage:.2f}%</li>"
                html_report_string += "</ul>"

                # Dynamically collect media files for this iteration
                json_file = None

                # Scan the output directory to identify the relevant files
                for file in os.listdir(output_path):
                    if file.startswith(str(iteration_number)):
                        if file.endswith("-affective.json"):
                            iteration_number = iteration_number + 1
                            json_file = file
                            break

                if json_file:
                    html_report_string += f'</br><a href="{json_file}" download>Download JSON File</a>'

        html_report_string += "</body></html>"

        # Write to HTML file
        html_file = open(output_path + "Full Report.html", 'w')
        html_file.write(html_report_string)
        html_file.close()

        return generated_report_string, score_psychomotor, score_cognitive

    def generate_summary_report(self, output_path, uuid_name, detected_errors, cognitive_answers, calculate_affective=False):
        self.detected_errors = detected_errors

        generated_report_string = _("psychomotor_module")

        generated_report_string += "\n"
        generated_report_string += "{:.2f}%\n".format(self.score_psychomotor_final)

        # New section for cognitive
        generated_report_string += "\n"
        generated_report_string += _("cognitive_module")

        generated_report_string += "\n"
        generated_report_string += "{:.2f}%\n".format(self.score_cognitive_final)  # 89 is max possible score.

        # New section for affective
        generated_report_string += "\n"
        generated_report_string += _("affective_module")

        generated_report_string += "\n"
        generated_report_string += self.majority_emotion_final

        # Write to file
        file = open(output_path + "Report.txt", 'w')
        file.write(generated_report_string)
        file.close()

        # Prepare summary json data
        report_data = {
            "psychomotor_module": {
                "score": round(self.score_psychomotor_final, 2),
            },
            "cognitive_module": {
                "score": round(self.score_cognitive_final, 2),
            },
            "affective_module": {
                "majority_emotion": self.majority_emotion_final,
            }
        }

        # Write to JSON file
        json_file_path = output_path + "Report.json"
        with open(json_file_path, 'w') as json_file:
            json.dump(report_data, json_file, indent=4)

        return generated_report_string, self.score_psychomotor_final, self.score_cognitive_final

    def deliver_reports(self, generated_reports):
        print(generated_reports[0])

    def calculate_emotion_percentages(self, emotions):
        total = len(emotions)
        emotion_counts = Counter(emotions)
        percentages = {emotion: (count / total) * 100 for emotion, count in emotion_counts.items()}
        return percentages, emotion_counts

    def load_and_process_files(self, directory):
        affective_data = {}
        overall_emotion_counts = Counter()

        for filename in os.listdir(directory):
            if filename.endswith('-affective.json'):
                # Extract the name part
                name = filename.rpartition('-')[0]
                file_path = os.path.join(directory, filename)
                with open(file_path, 'r') as file:
                    emotions = json.load(file)
                    percentages, emotion_counts = self.calculate_emotion_percentages(emotions)
                    affective_data[name] = percentages
                    overall_emotion_counts.update(emotion_counts)

        # Determine the majority emotion across all files
        if len(overall_emotion_counts.most_common(1)) > 0:
            majority_emotion, majority_count = overall_emotion_counts.most_common(1)[0]
        else:
            majority_emotion = "ND"

        return affective_data, majority_emotion

    def analyze_videos(self, output_path):
        # Run pose landmark detection
        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2, enable_segmentation=True) as pose:
            path_elements = os.listdir(output_path)
            for filename in path_elements:
                if filename.endswith('_raw.webm'):
                    affective_statuses_video = []

                    name = filename.removesuffix('_raw.webm')

                    capture_device = cv2.VideoCapture(output_path + filename)
                    fps = int(capture_device.get(cv2.CAP_PROP_FPS))

                    # While the webcam is opened...
                    num_frame = 0
                    analyze = True
                    while capture_device.isOpened():
                        # capture an image.
                        success, image = capture_device.read()

                        if not success:
                            break

                        # Only analyze each 0.5 seconds.
                        if (num_frame % round(fps/2)) == 0 or analyze:
                            # To improve performance, optionally mark the image as not writeable to pass by reference.
                            image.flags.writeable = False

                            # Change to RGB for mediapipe only.
                            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                            # Process the image using MediaPipe
                            pose_results = pose.process(image_rgb)

                            cv2.waitKey()
                            # If a pose has been detected extract segmentation mask
                            if pose_results.pose_landmarks is None:
                                # We could not process this frame, so next one will be processed if possible.
                                analyze = True
                            else:
                                # We could process this frame, so next one will adhere to frame restrictions.
                                analyze = False
                                # Image dimensions
                                height, width, channels = image.shape

                                # Get face region
                                nose_in_px = [pose_results.pose_landmarks.landmark[0].x * width,
                                              pose_results.pose_landmarks.landmark[0].y * height]
                                left_ear = [pose_results.pose_landmarks.landmark[8].x * width,
                                            pose_results.pose_landmarks.landmark[8].y * height]
                                right_ear = [pose_results.pose_landmarks.landmark[7].x * width,
                                             pose_results.pose_landmarks.landmark[7].y * height]
                                distance_ears = math.dist(left_ear, right_ear)

                                # Distance eyes outside
                                region = image[
                                         int(nose_in_px[1] - distance_ears):int(nose_in_px[1] + distance_ears),
                                         int(nose_in_px[0] - distance_ears):int(nose_in_px[0] + distance_ears)]

                                # Get affective status from face before blurring.
                                # Display the region of interest
                                inferred_status = self.affective.get_affective_status(region)

                                affective_statuses_video.append(inferred_status)

                        num_frame += 1

                    # Export affective statuses.
                    with open(output_path + name + "-affective.json", 'w') as f:
                        json.dump(affective_statuses_video, f, indent=4)

    @staticmethod
    def are_videos_analyzed(output_path):
        path_elements = os.listdir(output_path)
        for filename in path_elements:
            if filename.endswith('-affective.json'):
                return True
        return False

    @staticmethod
    def merge_json_files(input_folder, output_file):
        merged_data = {}
        frame_counter = 1  # Start numbering frames from 1 for consistency

        previous_movement_name = None
        previous_file_path = None
        movement_name = None
        # Loop through files in the specified folder
        for file_name in sorted(os.listdir(input_folder)):
            # Skip files that contain the string "affective" in their name
            if file_name.endswith('.json') and 'affective' not in file_name and "FullSet" not in file_name and "Report" not in file_name and "per_movement_score" not in file_name:
                # Get movement name.
                movement_name = file_name.split(".")[0].split("-")[1]

                if previous_movement_name is not None and movement_name != previous_movement_name:
                    # Get path to full file
                    file_path = os.path.join(input_folder, previous_file_path)

                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        print("Printing: ", previous_file_path)

                        # Adjust frame numbering for each JSON file
                        for frame in sorted(data.keys(), key=lambda f: int(f.split()[-1])):  # Sort frames within each file
                            new_frame_id = f"frame {frame_counter}"
                            merged_data[new_frame_id] = data[frame]
                            frame_counter += 1

                previous_file_path = file_name
                previous_movement_name = movement_name

        # Do the last one.
        # Get path to full file
        file_path = os.path.join(input_folder, previous_file_path)

        with open(file_path, 'r') as file:
            data = json.load(file)
            print("Printing: ", previous_file_path)

            # Adjust frame numbering for each JSON file
            for frame in sorted(data.keys(), key=lambda f: int(f.split()[-1])):  # Sort frames within each file
                new_frame_id = f"frame {frame_counter}"
                merged_data[new_frame_id] = data[frame]
                frame_counter += 1

        # Save the merged data to the specified output file
        with open(output_file, 'w') as outfile:
            json.dump(merged_data, outfile, indent=4)

        return merged_data

    @staticmethod
    def json_to_dataframe(merged_json, output_path):
        # Create a dictionary to hold the data for the DataFrame
        frame_data = {}

        # Iterate over each frame in the merged JSON
        for frame_id, landmarks in merged_json.items():
            # Create an entry for each landmark's attributes (x, y, z, visibility) in the frame
            for landmark, coords in landmarks.items():
                # For each coordinate (x, y, z, visibility), assign it to the appropriate column
                frame_data.setdefault(f"{landmark}_x", []).append(coords['x'])
                frame_data.setdefault(f"{landmark}_y", []).append(coords['y'])
                frame_data.setdefault(f"{landmark}_z", []).append(coords['z'])
                frame_data.setdefault(f"{landmark}_visibility", []).append(coords['visibility'])

        # Create a DataFrame from the dictionary, where keys are columns and values are lists (each list representing a column)
        dataframe = pd.DataFrame(frame_data)

        # Generate csv file.
        dataframe.to_csv(output_path + "FullSet.csv", index=False)

        return dataframe
