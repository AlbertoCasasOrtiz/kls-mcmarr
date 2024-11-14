from kls_mcmarr.mcmarr.analyze.MovementAnalyzer import MovementAnalyzer as _MovementAnalyzer
from kls_mcmarr.mcmarr.analyze.utils import *

from kls_mcmarr.kls.model.model import Model
from kls_mcmarr.kls.capture.global_values import GlobalValues


# Current max error score: 11
class ExtendedOutwardBlockAnalyzer(_MovementAnalyzer):

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

        # self.wrist = combine_close_points(modeled_movement, "RIGHT_WRIST_x", "RIGHT_WRIST_y")
        # self.elbow = combine_close_points(modeled_movement, "RIGHT_ELBOW_x", "RIGHT_ELBOW_y")

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
            store_error(self.errors,  self.movement_name + ": " + _("initial-position") + " - " + _("stage-not-finished") % {"stage_name": _("initial-position")} + ". " + _("body-part-never-moved-pos") % {"body_part": _("wrist"), "pos": _("left")} + ". " + _("ending-position-never-reached") + ".", 3, "b3e1")
            self.movement_completed = False
        elif not self.finished_transition_1:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "1"}} + ". " + _("body-part-never-surpassed-reference") % {"body_part": _("wrist"), "reference": _("elbow")} + ". " + _("ending-position-never-reached") + ".", 3, "b3e2")
            self.movement_completed = False
        elif not self.finished_transition_2:  # Should never happen, last frame should be always available.
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "1"}} + ". " + _("error-reaching-last-frame") + ". ", 3)
            self.movement_completed = False

        return self.movement_completed, self.errors

    def transitions(self):
        if self.current_rule == 2:
            self.transition1()
        elif self.current_rule == 3:
            self.transition2()

    def initial_pose(self):
        # Error: Right Wrist is not above Left Shoulder.
        if not above_of("RIGHT_WRIST", "LEFT_SHOULDER", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("shoulder")} + ".", 1)

        # Error: Right Wrist is not below EYES.
        if not below_of("RIGHT_WRIST", "RIGHT_EYE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("below"), "reference": _("eyes")} + ".", 1)

        # Error: Right Elbow is not in the vertical line of Center of the Body (within a threshold).
        # Calculate center area of body.
        center_hips = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] + self.modeled_movement["LEFT_HIP_x"][self.pos]) / 2)
        if not inside_area_of_point("RIGHT_ELBOW", center_hips, "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-in-reference") % {"body_part": _("elbow"), "reference": _("center-of-body")} + ".", 1)

        # # Error: Arm is not at 110 degrees (as seen from the front) (within a threshold).
        # if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 110, 25, self.modeled_movement, self.pos):
        #     store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "110"} + ".", 1)

        # Exit: The wrist goes left.
        if goes_left("RIGHT_WRIST", self.modeled_movement, self.pos, 3):
            if self.debug:
                # Error: Right Wrist is not above Left Shoulder.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["LEFT_SHOULDER" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "LEFT_SHOULDER"], self.modeled_movement_pixels, (0, self.pos+1), self.output_path + "- 1.Initial Position - Right Wrist is not above Left Shoulder.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not below EYES.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["RIGHT_EYE" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_EYE"], self.modeled_movement_pixels, (0, self.pos+1), self.output_path + "- 1.Initial Position - Right Wrist is below eyes.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Elbow is not in the vertical line of Center of the Body (within a threshold).
                def draw_function(ax):
                    ax.axvline(x=center_hips * GlobalValues.frame_width, color='red', linestyle='--', alpha=0.7)
                    ax.axvline(x=(center_hips * GlobalValues.frame_width) + self.distance_threshold*GlobalValues.frame_width, color='red', linestyle='--', alpha=0.7)
                    ax.axvline(x=(center_hips * GlobalValues.frame_width) - self.distance_threshold*GlobalValues.frame_width, color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_ELBOW", "RIGHT_HIP", "LEFT_HIP"], self.modeled_movement_pixels, (0, self.pos+1), self.output_path + "- 1.Initial Position - Right Elbow is not in the vertical line of Center of the Body.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit: The wrist goes left.
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3.Transition 2 - Exit The wrist goes left.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

            self.change_rule()
            self.finished_initial_position = True
            self.finished_initial_position_pos = self.pos

    def transition1(self):
        # Error: Right Wrist is not following a rectilinear horizontal trajectory (within a threshold).
        if not follows_line("RIGHT_WRIST", self.modeled_movement, self.pos, self.distance_threshold):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-following-trajectory") % {"body_part": _("wrist"), "trajectory_type": _("rectilinear")} + ".", 2, "b3e3")

        # Error: Right Elbow is not following a rectilinear horizontal trajectory (within a threshold).
        if not follows_line("RIGHT_ELBOW", self.modeled_movement, self.pos, self.distance_threshold):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-following-trajectory") % {"body_part": _("elbow"), "trajectory_type": _("rectilinear")} + ".", 1)

        # Error: Right Wrist is not above Right Shoulder.
        if not above_of("RIGHT_WRIST", "RIGHT_SHOULDER", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("shoulder")} + ".", 1)

        # Exit: Right Wrist is at left of Center of the Body.
        center_hips = [abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] + self.modeled_movement["LEFT_HIP_x"][self.pos]) / 2), abs((self.modeled_movement["RIGHT_HIP_y"][self.pos] + self.modeled_movement["LEFT_HIP_y"][self.pos]) / 2)]
        if at_left_of_point("RIGHT_WRIST", center_hips, self.modeled_movement, self.pos):
            if self.debug:
                def draw_function(ax):
                    # Get last position of a body part.
                    last_pos = self.modeled_movement_pixels.shape[0] - 1

                    # Get trajectory line from start of movement to end of movement.
                    first_pos_point = [self.modeled_movement_pixels["RIGHT_WRIST" + "_x"][0], self.modeled_movement_pixels["RIGHT_WRIST" + "_y"][0]]
                    last_pos_point = [self.modeled_movement_pixels["RIGHT_WRIST" + "_x"][last_pos], self.modeled_movement_pixels["RIGHT_WRIST" + "_y"][last_pos]]

                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1], last_pos_point[1]], color='red', linestyle='--', alpha=0.7)
                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1] - self.distance_threshold * GlobalValues.frame_height, last_pos_point[1] - self.distance_threshold * GlobalValues.frame_height], color='red', linestyle='--', alpha=0.7)
                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1] + self.distance_threshold * GlobalValues.frame_height, last_pos_point[1] + self.distance_threshold * GlobalValues.frame_height], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST"], self.modeled_movement_pixels, (self.finished_initial_position_pos, self.pos), self.output_path + "- 2.Transition 1 - Right Wrist is not following a rectilinear horizontal trajectory.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Elbow is not following a rectilinear horizontal trajectory.
                def draw_function(ax):
                    # Get last position of a body part.
                    last_pos = self.modeled_movement_pixels.shape[0] - 1

                    # Get trajectory line from start of movement to end of movement.
                    first_pos_point = [self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][0], self.modeled_movement_pixels["RIGHT_ELBOW" + "_y"][0]]
                    last_pos_point = [self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][last_pos], self.modeled_movement_pixels["RIGHT_ELBOW" + "_y"][last_pos]]

                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1], last_pos_point[1]], color='red', linestyle='--', alpha=0.7)
                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1] - self.distance_threshold * GlobalValues.frame_height, last_pos_point[1] - self.distance_threshold * GlobalValues.frame_height], color='red', linestyle='--', alpha=0.7)
                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1] + self.distance_threshold * GlobalValues.frame_height, last_pos_point[1] + self.distance_threshold * GlobalValues.frame_height], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_ELBOW"], self.modeled_movement_pixels, (self.finished_initial_position_pos, self.pos), self.output_path + "- 2.Transition 1 - Right Elbow is not following a rectilinear horizontal trajectory.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not above Right Shoulder.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["LEFT_SHOULDER" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_SHOULDER"], self.modeled_movement_pixels, (self.finished_initial_position_pos, self.pos), self.output_path + "- 2.Transition 1 - Right Wrist is not above Right Shoulder.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit: Right Wrist is at left of Center of the Body.
                def draw_function(ax):
                    ax.axvline(x=center_hips[0] * GlobalValues.frame_width, color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_HIP", "LEFT_HIP"], self.modeled_movement_pixels, (self.finished_initial_position_pos, self.pos), self.output_path + "- 2.Transition 1 - Exit Right Wrist is at left of Center of the Body.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

            self.change_rule()
            self.finished_transition_1 = True
            self.finished_transition_1_pos = self.pos

    def transition2(self):
        # Error: Right Wrist is not following a rectilinear horizontal trajectory (within a threshold).
        if not follows_line("RIGHT_WRIST", self.modeled_movement, self.pos, self.distance_threshold):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-following-trajectory") % {"body_part": _("wrist"), "trajectory_type": _("rectilinear")} + ".", 2, "b3e3")

        # Error: Right Elbow is not following a rectilinear horizontal trajectory (within a threshold).
        if not follows_line("RIGHT_ELBOW", self.modeled_movement, self.pos, self.distance_threshold):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-following-trajectory") % {"body_part": _("elbow"), "trajectory_type": _("rectilinear")} + ".", 1)

        # Error: Right Wrist is not above Right Shoulder.
        if not above_of("RIGHT_WRIST", "RIGHT_SHOULDER", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("shoulder")} + ".", 1)

        # Error: Right Wrist is not at left of Center of the Body.
        center_hips = [abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] + self.modeled_movement["LEFT_HIP_x"][self.pos]) / 2), abs((self.modeled_movement["RIGHT_HIP_y"][self.pos] + self.modeled_movement["LEFT_HIP_y"][self.pos]) / 2)]
        if not at_left_of_point("RIGHT_WRIST", center_hips, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-in-reference") % {"body_part": _("wrist"), "reference": _("elbow")} + ".", 1)

        # Exit: The last frame is reached.
        if self.pos == len(self.modeled_movement.index) - 2:
            if self.debug:
                # Error: Right Wrist is not following a rectilinear horizontal trajectory.
                def draw_function(ax):
                    # Get last position of a body part.
                    last_pos = self.modeled_movement_pixels.shape[0] - 1

                    # Get trajectory line from start of movement to end of movement.
                    first_pos_point = [self.modeled_movement_pixels["RIGHT_WRIST" + "_x"][0], self.modeled_movement_pixels["RIGHT_WRIST" + "_y"][0]]
                    last_pos_point = [self.modeled_movement_pixels["RIGHT_WRIST" + "_x"][last_pos], self.modeled_movement_pixels["RIGHT_WRIST" + "_y"][last_pos]]

                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1], last_pos_point[1]], color='red', linestyle='--', alpha=0.7)
                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1] - self.distance_threshold * GlobalValues.frame_height, last_pos_point[1] - self.distance_threshold * GlobalValues.frame_height], color='red', linestyle='--', alpha=0.7)
                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1] + self.distance_threshold * GlobalValues.frame_height, last_pos_point[1] + self.distance_threshold * GlobalValues.frame_height], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3.Transition 2 - Right Wrist is not following a rectilinear horizontal trajectory.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Elbow is not following a rectilinear horizontal trajectory.
                def draw_function(ax):
                    # Get last position of a body part.
                    last_pos = self.modeled_movement_pixels.shape[0] - 1

                    # Get trajectory line from start of movement to end of movement.
                    first_pos_point = [self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][0], self.modeled_movement_pixels["RIGHT_ELBOW" + "_y"][0]]
                    last_pos_point = [self.modeled_movement_pixels["RIGHT_ELBOW" + "_x"][last_pos], self.modeled_movement_pixels["RIGHT_ELBOW" + "_y"][last_pos]]

                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1], last_pos_point[1]], color='red', linestyle='--', alpha=0.7)
                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1] - self.distance_threshold * GlobalValues.frame_height, last_pos_point[1] - self.distance_threshold * GlobalValues.frame_height], color='red', linestyle='--', alpha=0.7)
                    ax.plot([first_pos_point[0], last_pos_point[0]], [first_pos_point[1] + self.distance_threshold * GlobalValues.frame_height, last_pos_point[1] + self.distance_threshold * GlobalValues.frame_height], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_ELBOW"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3.Transition 2 - Right Elbow is not following a rectilinear horizontal trajectory.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not above Right Shoulder.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["LEFT_SHOULDER" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_SHOULDER"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3.Transition 2 - Right Wrist is not above Right Shoulder.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not at left of Center of Body.
                def draw_function(ax):
                    ax.axvline(x=center_hips[0] * GlobalValues.frame_width, color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_HIP", "LEFT_HIP"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3.Transition 2 - Right Wrist is not at left of Center of Body.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit: The last frame is reached.
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_ELBOW"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3.Transition 2 - Exit The last frame is reached.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

            self.change_rule()
            self.finished_transition_2 = True
            self.finished_transition_2_pos = self.pos

    def ending_pose(self):
        # Error: Right Wrist is not above Right Shoulder.
        if not above_of("RIGHT_WRIST", "RIGHT_SHOULDER", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("shoulder")} + ".", 1)

        # Error: Right Wrist is not at left of Right Elbow.
        if not at_left_of("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("at-left"), "reference": _("elbow")} + ".", 1)

        # Error: Right Wrist is not below EYES.
        if not below_of("RIGHT_WRIST", "RIGHT_EYE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("below"), "reference": _("eyes")} + ".", 1)

        # # Error: Arm is not at 90 degrees (as seen from the front) (within a threshold).
        # if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 90, 25, self.modeled_movement, self.pos):
        #     store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "90"} + ".", 1)

        self.change_rule()
