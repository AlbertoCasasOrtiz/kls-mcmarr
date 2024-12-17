import os
import json
from pathlib import Path

import matplotlib.pyplot as plt
from collections import Counter

from kls_mcmarr.mcmarr.reports.MetaReportsMcmarr import MetaReportsMcmarr as _MetaReports


class MetaReports(_MetaReports):
    def __init__(self):
        super().__init__()

    def generate_meta_reports(self, session_path):
        # Get all folders inside of session_path sorted alphabetically
        folders = sorted([f for f in os.listdir(session_path) if os.path.isdir(os.path.join(session_path, f))])

        if not os.path.exists(session_path + os.sep + "metareport" + os.sep):
            os.makedirs(session_path + os.sep + "metareport" + os.sep)

        output_directory = session_path + os.sep + "metareport" + os.sep

        # Initialize lists to store scores
        psychomotor_scores = []
        cognitive_scores = []
        affective_scores = []
        sessions = []

        # For each folder...
        for folder in folders:
            folder_path = os.path.join(session_path, folder)
            report_file = os.path.join(folder_path, "Report.json")

            # Check if Report.json exists
            if os.path.exists(report_file):
                with open(report_file, 'r') as file:
                    try:
                        # Read and parse the JSON content
                        report = json.load(file)

                        # Extract scores
                        psychomotor_scores.append(report.get("psychomotor_module").get("score", 0.0))
                        cognitive_scores.append(report.get("cognitive_module").get("score", 0.0))
                        affective_scores.append(report.get("affective_module").get("majority_emotion", "N/A"))
                        sessions.append(folder)
                    except json.JSONDecodeError:
                        print(f"Error parsing JSON in {report_file}")
            # else:
            #     print(f"Report.json not found in {folder_path}")

        # Generate chart of psychomotor_module_score per session
        plt.figure(figsize=(10, 6))
        print(sessions)
        print(psychomotor_scores)
        plt.plot(sessions, psychomotor_scores, marker='o', label="Psychomotor Score")
        plt.title("Evolution of Psychomotor Module Score per Session")
        plt.xlabel("Session")
        plt.ylabel("Score")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.savefig(os.path.join(output_directory, "psychomotor_evolution.png"))
        plt.close()

        # Generate chart of cognitive_module_score per session
        plt.figure(figsize=(10, 6))
        plt.plot(sessions, cognitive_scores, marker='o', label="Cognitive Score", color="green")
        plt.title("Evolution of Cognitive Module Score per Session")
        plt.xlabel("Session")
        plt.ylabel("Score")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.savefig(os.path.join(output_directory, "cognitive_evolution.png"))
        plt.close()

        # Generate chart of affective_module_string per session
        plt.figure(figsize=(10, 6))
        plt.scatter(sessions, affective_scores, label="Affective Module", color="red")
        plt.title("Evolution of Affective Module per Session")
        plt.xlabel("Session")
        plt.ylabel("Affective State")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.savefig(os.path.join(output_directory, "affective_evolution.png"))
        plt.close()

        # Save data to JSON files
        psychomotor_data = {session: score for session, score in zip(sessions, psychomotor_scores)}
        cognitive_data = {session: score for session, score in zip(sessions, cognitive_scores)}
        affective_data = {session: status for session, status in zip(sessions, affective_scores)}

        with open(os.path.join(output_directory, "psychomotor_scores.json"), 'w') as f:
            json.dump(psychomotor_data, f, indent=4)

        with open(os.path.join(output_directory, "cognitive_scores.json"), 'w') as f:
            json.dump(cognitive_data, f, indent=4)

        with open(os.path.join(output_directory,"affective_statuses.json"), 'w') as f:
            json.dump(affective_data, f, indent=4)

        print("Charts have been generated and saved.")

        score_per_movement = []
        sessions = []

        # For each folder...
        for folder in folders:
            folder_path = os.path.join(session_path, folder)
            score_per_movement_file = os.path.join(folder_path, "per_movement_score.json")

            # Check if per_movement_score.json exists
            if os.path.exists(score_per_movement_file):
                with open(score_per_movement_file, 'r') as file:
                    try:
                        # Read and parse the JSON content
                        scores = json.load(file)

                        sessions.append(folder)
                        score_per_movement.append(scores)
                    except json.JSONDecodeError:
                        print(f"Error parsing JSON in {score_per_movement_file}")
            # else:
            #     print(f"score_per_movement_file.json not found in {folder_path}")

        # Transform data: Map movements to their scores across sessions
        movement_scores = {}
        for session, scores in zip(sessions, score_per_movement):
            for movement_score in scores:
                for movement, score in movement_score.items():
                    if movement not in movement_scores:
                        movement_scores[movement] = []
                    movement_scores[movement].append((session, score))


        # Data for JSON output
        output_data = {}

        for movement, scores in movement_scores.items():
            sessions_sorted, scores_sorted = zip(*sorted(scores))  # Sort by session names
            plt.figure(figsize=(10, 6))
            plt.plot(sessions_sorted, scores_sorted, marker='o', label=movement, color="blue")
            plt.title(f"Evolution of {movement} per Session")
            plt.xlabel("Session")
            plt.ylabel("Score")
            plt.xticks(rotation=45)
            plt.legend()
            plt.grid()
            plt.tight_layout()

            # Save the plot
            chart_path = os.path.join(output_directory, f"{movement}_evolution.png")
            plt.savefig(chart_path)
            plt.close()

            # Add to JSON data
            for session, score in scores:
                if session not in output_data:
                    output_data[session] = {}
                output_data[session][movement] = score

        # Save the JSON file
        output_json_path = os.path.join(output_directory, "scores_per_session.json")
        with open(output_json_path, 'w') as json_file:
            json.dump(output_data, json_file, indent=4)

    def get_metareport_values(self, session_path, max_num_sessions=3):
        meta_report_dir = session_path + os.sep + "metareport" + os.sep

        # Define file paths
        psychomotor_file = meta_report_dir + "psychomotor_scores.json"
        cognitive_file = meta_report_dir + "cognitive_scores.json"
        affective_file = meta_report_dir + "affective_statuses.json"

        # Initialize default values
        default_values = {
            "mean_previous_psychomotor_score": 0,
            "mean_previous_cognitive_score": 0,
            "majoritary_previous_emotion": "Neutral"
        }

        # Check for missing files and return defaults if any file is missing
        if not os.path.exists(psychomotor_file) or not os.path.exists(cognitive_file) or not os.path.exists(affective_file):
            return default_values

        # Load the JSON files
        with open(psychomotor_file, "r") as f:
            psychomotor_scores = json.load(f)
        with open(cognitive_file, "r") as f:
            cognitive_scores = json.load(f)
        with open(affective_file, "r") as f:
            affective_statuses = json.load(f)

        # Sort sessions by the session keys (which represent timestamps)
        sessions = sorted(psychomotor_scores.keys(), reverse=True)

        if not sessions:
            # If there are no sessions, return the default values
            return default_values

        # Use the last `max_num_sessions` sessions or all available sessions if fewer
        recent_sessions = sessions[:max_num_sessions]

        # Calculate the mean psychomotor score
        recent_psychomotor_scores = [psychomotor_scores[session] for session in recent_sessions]
        mean_previous_psychomotor_score = sum(recent_psychomotor_scores) / len(recent_psychomotor_scores)

        # Calculate the mean cognitive score
        recent_cognitive_scores = [cognitive_scores[session] for session in recent_sessions]
        mean_previous_cognitive_score = sum(recent_cognitive_scores) / len(recent_cognitive_scores)

        # Calculate the majority affective status
        recent_affections = [affective_statuses[session] for session in recent_sessions]
        emotion_count = Counter(recent_affections)
        majoritary_previous_emotion = emotion_count.most_common(1)[0][0]

        # Return the results
        return {
            "mean_previous_psychomotor_score": mean_previous_psychomotor_score,
            "mean_previous_cognitive_score": mean_previous_cognitive_score,
            "majoritary_previous_emotion": majoritary_previous_emotion
        }