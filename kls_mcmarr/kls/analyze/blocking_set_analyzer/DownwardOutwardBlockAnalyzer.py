from matplotlib import pyplot as plt

from kls_mcmarr.kls.capture.global_values import GlobalValues
from kls_mcmarr.mcmarr.analyze.MovementAnalyzer import MovementAnalyzer as _MovementAnalyzer
from kls_mcmarr.mcmarr.analyze.utils import *

from kls_mcmarr.kls.model.model import Model
from kls_mcmarr.kls.capture.global_values import GlobalValues

# Current max error score: 11
class DownwardOutwardBlockAnalyzer(_MovementAnalyzer):

    def __init__(self, modeled_movement, movement_name, pos=0, debug=False, video_path=None, output_path=None):
        super().__init__(modeled_movement, movement_name, pos)

        self.debug = debug
        self.video_path = video_path
        self.output_path = output_path
        if self.debug:
            self.modeled_movement_pixels = convert_to_pixel_coordinates(modeled_movement, GlobalValues.frame_width, GlobalValues.frame_height)
            self.model = Model(output_path=output_path)

        self.finished_initial_position = False
        self.finished_initial_position_pos = -1
        self.finished_transition_1 = False
        self.finished_transition_1_pos = -1
        self.finished_transition_2 = False
        self.finished_transition_2_pos = -1

        self.start_transition_1 = 0

        self.center_elbow = None
        self.first_wrist_distance = None

        self.elbow_close_to_body = False

        self.combined_threshold = calculate_distance_threshold(modeled_movement, "RIGHT_WRIST_x", "RIGHT_WRIST_y", 0, 0.1)

        self.distance_threshold = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] - self.modeled_movement["LEFT_HIP_x"][self.pos]) / 2)
        self.distance_threshold_large = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] - self.modeled_movement["LEFT_HIP_x"][self.pos]) / 2) * 2.5
        # Adapted to the diagonal, so the aspect ratio does not affect.
        self.distance_threshold_pixels = self.distance_threshold * math.sqrt(GlobalValues.frame_width ** 2 + GlobalValues.frame_height ** 2)

    def apply_rules(self):
        while not self.finished_analysis:
            if self.current_rule == 1:
                self.initial_pose()
            elif 2 <= self.current_rule <= 3:
                self.transitions()
            elif self.current_rule == 4 and self.pos == len(self.modeled_movement.index) - 1:
                self.ending_pose()
            else:
                pass
            self.pos = self.pos + 1
            if self.pos >= len(self.modeled_movement.index):
                self.finished_analysis = True

        # Check if the different positions and transitions have been completed.
        if not self.finished_initial_position:
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("stage-not-finished") % {"stage_name": _("initial-position")} + ". " + _("body-part-never-moved-pos") % {"body_part": _("wrist"), "pos": _("right")} + ". " + _("ending-position-never-reached") + ".", 3, "b4e1")
            self.movement_completed = False
        elif not self.finished_transition_1:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "1"}} + ". " + _("error-reaching-last-frame") + ". " + _("ending-position-never-reached") + ".", 3, "b4e2")
            self.movement_completed = False
        elif not self.finished_transition_2:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "2"}} + ". " + _("error-reaching-last-frame") + ". " + _("ending-position-never-reached") + ".", 3, "b4e2")
            self.movement_completed = False

        return self.movement_completed, self.errors

    def transitions(self):
        if self.current_rule == 2:
            self.transition1()
        elif self.current_rule == 3:
            self.transition2()

    def initial_pose(self):
        # Error: Right Wrist is not above Right Shoulder.
        if not above_of("RIGHT_WRIST", "RIGHT_SHOULDER", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("shoulder")} + ".", 1)

        # Error: Right Wrist is not at left of Right Elbow.
        if not at_left_of("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("at-left"), "reference": _("elbow")} + ".", 1)

        # Error: Right Wrist is not below Eyes.
        if not below_of("RIGHT_WRIST", "RIGHT_EYE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("below"), "reference": _("eyes")} + ".", 1)

        # # Error: Arm is not at 90 degrees (as seen from the front) (within a threshold).
        # if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 90, 25, self.modeled_movement, self.pos):
        #     store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "90"} + ".", 1)

        # Exit: Right Wrist goes right.
        if goes_right("RIGHT_WRIST", self.modeled_movement, self.pos, 3):
            if self.debug:

                # Error: Right Wrist is not above Right Shoulder.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["LEFT_SHOULDER" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_SHOULDER"], self.modeled_movement_pixels, (0, self.pos+1), self.output_path + "- 1.Initial Position - Right Wrist is not above Right Shoulder.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not at left of Right Elbow.
                def draw_function(ax):
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "LEFT_SHOULDER"], self.modeled_movement_pixels, (0, self.pos+1), self.output_path + "- 1.Initial Position - Right Wrist is not at left of Right Elbow.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not below EYES.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["RIGHT_EYE" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_EYE"], self.modeled_movement_pixels, (0, self.pos + 1), self.output_path + "- 1.Initial Position - Right Wrist is below eyes.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

            self.change_rule()
            self.finished_initial_position = True
            self.finished_initial_position_pos = self.pos

    def transition1(self):
        # First, lets calculate center of elbow.
        if self.center_elbow is None:
            elbow_points = []
            for i in range(self.start_transition_1, len(self.modeled_movement.index)):
                elbow_points.append([self.modeled_movement["RIGHT_ELBOW_x"][i], self.modeled_movement["RIGHT_ELBOW_y"][i]])
            self.center_elbow = calculate_center(elbow_points)

        # Now, lets calculate wrist distance from wrist to center of elbow.
        if self.first_wrist_distance is None:
            # Needs to be converted to pixels to avoid deformation of resizing to values between 0 and 1.
            first_wrist_position = [self.modeled_movement["RIGHT_WRIST_x"][self.start_transition_1] * GlobalValues.frame_width,
                                    self.modeled_movement["RIGHT_WRIST_y"][self.start_transition_1] * GlobalValues.frame_height]
            center_elbow_pixels = [self.center_elbow[0] * GlobalValues.frame_width,
                                   self.center_elbow[1] * GlobalValues.frame_height]
            self.first_wrist_distance = math.dist(center_elbow_pixels, first_wrist_position)

        # Error: Right Wrist does not follow a clockwise trajectory.
        # We check the positions are not too close to each other to avoid accounting small variations at the end of the movement.
        if self.pos != len(self.modeled_movement.index) - 1 and abs(self.modeled_movement["RIGHT_WRIST_x"][self.pos] - self.modeled_movement["RIGHT_WRIST_x"][self.pos-1]) > self.modeled_movement["RIGHT_WRIST_x"].diff().mean():
            clockwise = follows_circular_clockwise_trajectory("RIGHT_WRIST", "RIGHT_ELBOW", self.combined_threshold, self.modeled_movement, self.pos)
            if clockwise is not None and not clockwise:
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-following-trajectory") % {"body_part": _("wrist"), "trajectory_type": _("clockwise")} + ".", 2, "b4e3")

        # Error: Right Wrist does not follow a circular trajectory (within a threshold).
        # Needs to be converted to pixels to avoid deformation of resizing to values between 0 and 1.
        current_wrist_position = [self.modeled_movement["RIGHT_WRIST_x"][self.pos] * GlobalValues.frame_width,
                                  self.modeled_movement["RIGHT_WRIST_y"][self.pos] * GlobalValues.frame_height]
        center_elbow_pixels = [self.center_elbow[0] * GlobalValues.frame_width,
                               self.center_elbow[1] * GlobalValues.frame_height]
        current_wrist_distance = math.dist(current_wrist_position, center_elbow_pixels)
        if abs(self.first_wrist_distance - current_wrist_distance) > self.distance_threshold_pixels:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-following-trajectory") % {"body_part": _("wrist"), "trajectory_type": _("circular")} + ".", 2, "b4e3")

        # Error: Right Elbow is not anchored to the Right Hip at some point.
        if inside_area("RIGHT_ELBOW", "RIGHT_HIP", "x", self.distance_threshold, self.modeled_movement, self.pos):
            self.elbow_close_to_body = True

        # Exit: Right Wrist is below and in the same vertical as Right Elbow.
        if inside_area("RIGHT_WRIST", "RIGHT_ELBOW", "x", self.distance_threshold, self.modeled_movement, self.pos)\
                and below_of("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos):
            if self.debug:
                # Error: Right Wrist does not follow a circular trajectory.
                def draw_function(ax):
                    # Drawing a vertical line for reference
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][self.pos], color='red',
                               linestyle='--', alpha=0.7)

                    # Define center and radius for the circle
                    center = (self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][self.pos], self.modeled_movement_pixels["RIGHT_ELBOW" + "_y"][self.pos])
                    radius = current_wrist_distance
                    # Create and add the circle
                    circle = plt.Circle(center, radius, color='blue', fill=False, linestyle='--', alpha=0.7)
                    ax.add_patch(circle)

                    radius = current_wrist_distance + self.distance_threshold * ((GlobalValues.frame_width + GlobalValues.frame_height) / 2) + 50
                    # Create and add the circle
                    circle = plt.Circle(center, radius, color='blue', fill=False, linestyle='--', alpha=0.7)
                    ax.add_patch(circle)

                    # Create and add the circle
                    radius = current_wrist_distance - self.distance_threshold * ((GlobalValues.frame_width + GlobalValues.frame_height) / 2) - 50
                    # Create and add the circle
                    circle = plt.Circle(center, radius, color='blue', fill=False, linestyle='--', alpha=0.7)
                    ax.add_patch(circle)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_ELBOW"], self.modeled_movement_pixels, (self.finished_initial_position_pos, self.pos), self.output_path + "- 2. Transition 1 -  Right Wrist does not follow a circular clockwise trajectory.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit: Right Elbow is not anchored to the Right Hip at some point.
                def draw_function(ax):
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_HIP" + "_x"][self.pos], color='red', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_HIP" + "_x"][self.pos] + self.distance_threshold*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_HIP" + "_x"][self.pos] - self.distance_threshold*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_ELBOW", "RIGHT_HIP"], self.modeled_movement_pixels, (self.finished_initial_position_pos, self.pos), self.output_path + "- 2. Transition 1 - Right Elbow is not anchored to the Right Hip at some point.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit: Right Wrist is below and in the same vertical as Right Elbow.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["RIGHT_ELBOW" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][self.pos], color='red', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][self.pos] + self.distance_threshold*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][self.pos] - self.distance_threshold*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_ELBOW"], self.modeled_movement_pixels, (self.finished_initial_position_pos, self.pos), self.output_path + "- 2. Transition 1 - Exit Right Wrist is below and in the same vertical as Right Elbow.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

            # Check here if the elbow was at some point anchored to the body.
            if not self.elbow_close_to_body:
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-anchored") % {"body_part": _("elbow")} + ".", 1)

            self.change_rule()
            self.finished_transition_1 = True
            self.finished_transition_1_pos = self.pos

    def transition2(self):
        # Error: Right Wrist and Right Elbow are not in the same vertical line.
        if not inside_area("RIGHT_WRIST", "RIGHT_ELBOW", "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-parts-not-same-line") % {"body_part_1": _("wrist"), "body_part_2": _("elbow"), "line_type": _("horizontal")} + ".", 1)

        # Error: Right Wrist is not near Right Hip (within a threshold).
        if not inside_area("RIGHT_WRIST", "RIGHT_HIP", "x", self.distance_threshold_large, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-far-from-reference") % {"body_part": _("wrist"), "reference": _("hip")} + ".", 1)

        # # Error: Arm is not at 180 degrees (as seen from the front) (within a threshold).
        # if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 180, 25, self.modeled_movement, self.pos):
        #     store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "3"} + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "180"} + ".", 1)

        # Exit: The last frame is reached.
        if self.pos == len(self.modeled_movement.index) - 2:
            if self.debug:

                # Error: Right Wrist and Right Elbow are not in the same vertical line.
                def draw_function(ax):
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][self.pos], color='red', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][self.pos] + self.distance_threshold*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][self.pos] - self.distance_threshold*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_ELBOW"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3. Transition 2 - Right Wrist and Right Elbow are not in the same vertical line.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not near Right Hip (within a threshold).
                def draw_function(ax):
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_HIP" + "_x"][self.pos], color='red', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_HIP" + "_x"][self.pos] + self.distance_threshold_large*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_HIP" + "_x"][self.pos] - self.distance_threshold_large*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_HIP"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3. Transition 2 - Right Wrist is not near Right Hip (within a threshold).mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit: The last frame is reached.
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_ELBOW"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3.Transition 2 - Exit The last frame is reached.mp4", GlobalValues.frame_width, GlobalValues.frame_height)

            self.change_rule()
            self.finished_transition_2 = True
            self.finished_transition_2_pos = self.pos

    def ending_pose(self):
        # Error: Right Wrist and Right Elbow are not in the same vertical line.
        if not inside_area("RIGHT_WRIST", "RIGHT_ELBOW", "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-parts-not-same-line") % {"body_part_1": _("wrist"), "body_part_2": _("elbow"), "line_type": _("horizontal")} + ".", 1)

        # Error: Right Wrist is not at left of Right Hip (within a threshold).
        if not at_left_of("RIGHT_WRIST", "RIGHT_HIP", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-distance-body-part") % {"body_part_1": _("wrist"), "body_part_2": _("body"), "distance": _("one-punch")} + ".", 1)

        # Error: Right Wrist is not near Right Hip (within a threshold).
        if not inside_area("RIGHT_WRIST", "RIGHT_HIP", "x", self.distance_threshold_large, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-distance-body-part") % {"body_part_1": _("wrist"), "body_part_2": _("body"), "distance": _("one-punch")} + ".", 1)

        # # Error: Arm is not at 180 degrees (as seen from the front) (within a threshold).
        # if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 180, 25, self.modeled_movement, self.pos):
        #     store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "180"} + ".", 1)

        self.change_rule()
