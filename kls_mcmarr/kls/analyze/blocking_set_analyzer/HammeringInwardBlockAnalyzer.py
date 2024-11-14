from kls_mcmarr.mcmarr.analyze.MovementAnalyzer import MovementAnalyzer as _MovementAnalyzer
from kls_mcmarr.mcmarr.analyze.utils import *

from kls_mcmarr.kls.model.model import Model
from kls_mcmarr.kls.capture.global_values import GlobalValues


# Current max error score: 12
class HammeringInwardBlockAnalyzer(_MovementAnalyzer):

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

        self.distance_threshold = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] - self.modeled_movement["LEFT_HIP_x"][self.pos]) / 2)

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
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("stage-not-finished") % {"stage_name": _("initial-position")} + ". " + _("body-part-never-moved-pos") % {"body_part": _("wrist"), "pos": _("down-and-away-from-center-body")} + ". " + _("ending-position-never-reached") + ".", 3, "b2e1")
            self.movement_completed = False
        elif not self.finished_transition_1:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "1"}} + ". " + _("body-part-never-pos-relative-to") % {"body_part": _("wrist"), "reference_part": _("horizontal-line-eyes"), "pos": _("down")} + ". " + _("ending-position-never-reached") + ".", 3, "b2e2")
            self.movement_completed = False
        elif not self.finished_transition_2:  # Should never happen, last frame should be always available.
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "1"}} + ". " + _("error-reaching-last-frame") + ". " + _("ending-position-never-reached") + ".", 3)
            self.movement_completed = False

        return self.movement_completed, self.errors

    def transitions(self):
        if self.current_rule == 2:
            self.transition1()
        elif self.current_rule == 3:
            self.transition2()

    def initial_pose(self):
        # Error: Right Wrist is not above Right Eye.
        if not above_of("RIGHT_WRIST", "RIGHT_EYE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("head")} + ".", 1)

        # Error: Right Wrist is not above Right Elbow.
        if not above_of("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("elbow")} + ".", 1)

        # Error: Right Elbow is not near Ear (within a threshold).
        if not inside_area("RIGHT_ELBOW", "RIGHT_EAR", "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-far-from-reference") % {"body_part": _("elbow"), "reference": _("ear")} + ".", 1)

        # Error: Right Wrist is not at right of Nose.
        if not at_right_of("RIGHT_WRIST", "NOSE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-crossing-reference") % {"body_part": _("wrist"), "reference": _("nose")} + ".", 1)

        # Error: Right Wrist is not at left of Left Shoulder.
        if not at_left_of("RIGHT_WRIST", "LEFT_SHOULDER", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-beyond-reference") % {"body_part": _("wrist"), "reference": _("shoulder")} + ".", 1)

        # # Error: Arm is not at 125 degrees (as seen from the front) (within a threshold).
        # if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 125, 25, self.modeled_movement, self.pos):
        #     store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "125"} + ".", 1)

        # Exit: Right Wrist goes down and away from Center of the Body.
        if goes_down("RIGHT_WRIST", self.modeled_movement, self.pos, 1) and goes_right("RIGHT_WRIST", self.modeled_movement, self.pos, 1):
            if self.debug:

                # Error: Right Wrist is not above Right Elbow.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["RIGHT_ELBOW" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_ELBOW"], self.modeled_movement_pixels, (0, self.pos), self.output_path + "- 1.Initial Position - Right Wrist is not above Right Elbow.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not above Right Eye.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["RIGHT_EYE" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_EYE"], self.modeled_movement_pixels, (0, self.pos), self.output_path + "- 1.Initial Position - Right Wrist is not above Right Eye.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Elbow is far from Right Ear (within a threshold).
                def draw_function(ax):
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_EAR" + "_x"][self.pos], color='red', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_EAR" + "_x"][self.pos] + self.distance_threshold*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_EAR" + "_x"][self.pos] - self.distance_threshold*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_ELBOW", "RIGHT_EAR"], self.modeled_movement_pixels, (0, self.pos), self.output_path + "- 1.Initial Position - Right Elbow is far from Right Ear.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not at right of Nose.
                def draw_function(ax):
                    ax.axvline(x=self.modeled_movement_pixels["NOSE" + "_x"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "NOSE"], self.modeled_movement_pixels, (0, self.pos), self.output_path + "- 1.Initial Position - Right Wrist is not at right of Nose.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not at left of Left Shoulder.
                def draw_function(ax):
                    ax.axvline(x=self.modeled_movement_pixels["LEFT_SHOULDER" + "_x"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "LEFT_SHOULDER"], self.modeled_movement_pixels, (0, self.pos), self.output_path + "- 1.Initial Position - Right Wrist is not at left of Left Shoulder.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit: Right Wrist goes down and away from Center of the Body.
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_HIP", "LEFT_HIP"], self.modeled_movement_pixels, (0, self.pos), self.output_path + "- 1.Initial Position - Exit Right Wrist goes down and away from Center of the Body.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

            self.change_rule()
            self.finished_initial_position = True
            self.finished_initial_position_pos = self.pos

    def transition1(self):
        # Error: Right Wrist is not following a rectilinear trajectory to its final position (within a threshold).
        if not follows_line("RIGHT_WRIST", self.modeled_movement, self.pos, self.distance_threshold):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-following-trajectory") % {"body_part": _("wrist"), "trajectory_type": _("rectilinear")} + ".", 2, "b2e3")

        # Exit: Right Wrist is below EYES.
        if below_of("RIGHT_WRIST", "RIGHT_EYE", self.modeled_movement, self.pos):
            if self.debug:
                # Error: Right Wrist is not following a rectilinear trajectory to its final position (within a threshold).
                def draw_function(ax):

                    # Get last position of a body part.
                    last_pos = self.modeled_movement_pixels.shape[0] - 1

                    # Get trajectory line from start of movement to end of movement.
                    first_pos_point = [self.modeled_movement_pixels["RIGHT_WRIST" + "_x"][0], self.modeled_movement_pixels["RIGHT_WRIST" + "_y"][0]]
                    last_pos_point = [self.modeled_movement_pixels["RIGHT_WRIST" + "_x"][last_pos], self.modeled_movement_pixels["RIGHT_WRIST" + "_y"][last_pos]]

                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1], last_pos_point[1]], color='red', linestyle='--', alpha=0.7)
                    ax.plot([first_pos_point[0] - self.distance_threshold * GlobalValues.frame_width, last_pos_point[0] - self.distance_threshold * GlobalValues.frame_width],
                            [first_pos_point[1], last_pos_point[1]],
                            color='red', linestyle='--', alpha=0.7)
                    ax.plot([first_pos_point[0] + self.distance_threshold * GlobalValues.frame_width, last_pos_point[0] + self.distance_threshold * GlobalValues.frame_width],
                            [first_pos_point[1], last_pos_point[1]],
                            color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST"], self.modeled_movement_pixels, (self.finished_initial_position_pos, self.pos), self.output_path + "- 2.Transition 1 - Right Wrist is not following a rectilinear trajectory to its final position.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit: Right Wrist is below EYES.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["RIGHT_EYE" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_EYE"], self.modeled_movement_pixels, (self.finished_initial_position_pos, self.pos), self.output_path + "- 2.Transition 1 - Exit Right Wrist is below eyes.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

            self.change_rule()
            self.finished_transition_1 = True
            self.finished_transition_1_pos = self.pos

    def transition2(self):
        # Error: Right Wrist is not above Left Shoulder.
        if not above_of("RIGHT_WRIST", "LEFT_SHOULDER", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("shoulder")} + ".", 1)

        # Error: Right Wrist is not below EYES.
        if not below_of("RIGHT_WRIST", "RIGHT_EYE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("below"), "reference": _("eyes")} + ".", 1)

        # Exit: The last frame is reached.
        if self.pos == len(self.modeled_movement.index) - 2:
            if self.debug:

                # Error: Right Wrist is not above Left Shoulder.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["LEFT_SHOULDER" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "LEFT_SHOULDER"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3.Transition 2 - Right Wrist is not above Left Shoulder.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not below EYES.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["RIGHT_EYE" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_EYE"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3.Transition 2 - Right Wrist is below eyes.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit: The last frame is reached.
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_ELBOW"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3.Transition 2 - Exit The last frame is reached.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

            self.change_rule()
            self.finished_transition_2 = True
            self.finished_transition_2_pos = self.pos

    def ending_pose(self):
        # Error: Right Wrist is not above Left Shoulder.
        if not above_of("RIGHT_WRIST", "LEFT_SHOULDER", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("shoulder")} + ".", 1)

        # Error: Right Wrist is not below EYES.
        if not below_of("RIGHT_WRIST", "RIGHT_EYE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("below"), "reference": _("eyes")} + ".", 1)

        # Error: Right Elbow is not in the vertical line of Center of the Body (within a threshold).
        # Calculate center area of body.
        center_hips = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] + self.modeled_movement["LEFT_HIP_x"][self.pos]) / 2)
        if not inside_area_of_point("RIGHT_ELBOW", center_hips, "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-parts-not-same-line") % {"body_part_1": _("elbow"), "body_part_2": _("center-of-body"), "line_type": _("vertical")} + ".", 1)

        # # Error: Arm is not at 110 degrees (as seen from the front) (within a threshold).
        # if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 110, 25, self.modeled_movement, self.pos):
        #     store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "110"} + ".", 1)

        self.change_rule()
