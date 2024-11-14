from kls_mcmarr.mcmarr.analyze.MovementAnalyzer import MovementAnalyzer as _MovementAnalyzer
from kls_mcmarr.mcmarr.analyze.utils import *

from kls_mcmarr.kls.model.model import Model
from kls_mcmarr.kls.capture.global_values import GlobalValues

# Current max error score: 20
class UpwardBlockAnalyzer(_MovementAnalyzer):

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
        self.finished_transition_3 = False
        self.finished_transition_3_pos = -1
        self.finished_transition_4 = False
        self.finished_transition_4_pos = -1

        self.distance_threshold = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] - self.modeled_movement["LEFT_HIP_x"][self.pos]) / 2)

    def apply_rules(self):
        while not self.finished_analysis:
            if self.current_rule == 1:
                self.initial_pose()
            elif 2 <= self.current_rule <= 5:
                self.transitions()
            elif self.current_rule == 6 and self.pos == len(self.modeled_movement.index) - 1:
                self.ending_pose()
            else:
                pass
            self.pos = self.pos + 1
            if self.pos >= len(self.modeled_movement.index):
                self.finished_analysis = True

        # Check if the different positions and transitions have been completed.
        if not self.finished_initial_position:
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("stage-not-finished") % {"stage_name": _("initial-position")} + ". " +  _("body-part-never-pos-reference") % {"body_part": _("wrist"), "pos": _("inside"), "reference": _("center-of-body")} + ". " + _("ending-position-never-reached") + ".", 3, "b1e1")
            self.movement_completed = False
        elif not self.finished_transition_1:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "1"}} + ". " + _("body-part-never-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("plexus")} + ". " + _("ending-position-never-reached") + ".", 3, "b1e2")
            self.movement_completed = False
        elif not self.finished_transition_2:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "1"}} + ". " + _("body-part-never-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("nose")} + ". " + _("ending-position-never-reached") + ".", 3, "b1e2")
            self.movement_completed = False
        elif not self.finished_transition_3:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "3"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "3"}} + ". " + _("body-part-never-stopped-going-pos") % {"body_part": _("wrist"), "pos": _("up")} + ". " + _("ending-position-never-reached") + ".", 3, "b1e3")
            self.movement_completed = False
        elif not self.finished_transition_4:  # Should never happen, last frame should be always available.
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "4"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "4"}} + ". " + _("error-reaching-last-frame") + ". ", 3)
            self.movement_completed = False

        return self.movement_completed, self.errors

    def transitions(self):
        if self.current_rule == 2:
            self.transition1()
        elif self.current_rule == 3:
            self.transition2()
        elif self.current_rule == 4:
            self.transition3()
        elif self.current_rule == 5:
            self.transition4()

    def initial_pose(self):
        # Error: Right  Wrist is not above Right Hip.
        if not above_of("RIGHT_WRIST", "RIGHT_HIP", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("hip")} + ".", 1)

        # Error: Right Wrist is not below Solar Plexus.
        plexus_point = get_plexus_point(self.modeled_movement, self.pos)
        if not below_of_point("RIGHT_WRIST", plexus_point, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("below"), "reference": _("solar-plexus")} + ".", 1)

        # Error: Right Wrist is far from Right Hip (within a threshold).
        if not inside_area("RIGHT_WRIST", "RIGHT_HIP", "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-far-from-reference") % {"body_part": _("wrist"), "reference": _("body")} + ".", 1)

        # Exit: Right Wrist is inside of body.
        right_shoulder_point = [self.modeled_movement["RIGHT_SHOULDER_x"][self.pos], self.modeled_movement["RIGHT_SHOULDER_y"][self.pos]]
        right_wrist_point = [self.modeled_movement["RIGHT_HIP_x"][self.pos], self.modeled_movement["RIGHT_HIP_y"][self.pos]]
        middle_shoulder_hip = calculate_center([right_shoulder_point, right_wrist_point])
        if at_right_of_point("RIGHT_WRIST", middle_shoulder_hip, self.modeled_movement, self.pos):
            if self.debug:
                # Error: Right Wrist is not above Right Hip.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["RIGHT_HIP" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_HIP"], self.modeled_movement_pixels, (0, self.pos), self.output_path + "- 1.Initial Position - Right  Wrist is not above Right Hip.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not below Solar Plexus.
                def draw_function(ax):
                    ax.axhline(y=plexus_point[1] * GlobalValues.frame_height, color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST"], self.modeled_movement_pixels, (0, self.pos), self.output_path + "- 1.Initial Position - Right Wrist is not below Solar Plexus.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is far from Right Hip (within a threshold).
                def draw_function(ax):
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_HIP" + "_x"][self.pos], color='red', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_HIP" + "_x"][self.pos] + self.distance_threshold*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_HIP" + "_x"][self.pos] - self.distance_threshold*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_HIP"], self.modeled_movement_pixels, (0, self.pos), self.output_path + "- 1.Initial Position - Right Wrist is far from Right Hip.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit: Right Wrist is inside of body.
                def draw_function(ax):
                    ax.axvline(x=middle_shoulder_hip[0]*GlobalValues.frame_width, color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_HIP", "RIGHT_SHOULDER"], self.modeled_movement_pixels, (0, self.pos), self.output_path + "- 1.Initial Position - Exit Right Wrist is inside of body.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

            self.change_rule()
            self.finished_initial_position = True
            self.finished_initial_position_pos = self.pos

    def transition1(self):
        # Error: Right Wrist is not moving upwards.
        if not goes_up("RIGHT_WRIST", self.modeled_movement, self.pos, 3):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-going-pos") % {"body_part": _("wrist"), "pos": _("up")} + ".", 1)

        # Error: Right Wrist is not moving towards Center of the Body.
        if not goes_right("RIGHT_WRIST", self.modeled_movement, self.pos, 3):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-going-pos") % {"body_part": _("wrist"), "pos": _("center-of-body")} + ".", 1)

        # Exit : Right Wrist is above the plexus.
        # Calculate plexus point
        plexus = get_plexus_point(self.modeled_movement, self.pos)
        if above_of_point("RIGHT_WRIST", plexus, self.modeled_movement, self.pos):
            if self.debug:
                # Exit : Right Wrist is above the plexus.
                def draw_function(ax):
                    ax.axhline(y=plexus[1] * GlobalValues.frame_height, color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST"], self.modeled_movement_pixels, (self.finished_initial_position_pos, self.pos), self.output_path + "- 2.Transition 1 - Exit Right Wrist is above the plexus.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

            self.change_rule()
            self.finished_transition_1 = True
            self.finished_transition_1_pos = self.pos

    def transition2(self):
        # Error: Right Wrist is not moving upwards.
        if not goes_up("RIGHT_WRIST", self.modeled_movement, self.pos, 3):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-going-pos") % {"body_part": _("wrist"), "pos": _("up")} + ".", 1)

        # Error: Right Wrist is away from Center of the Body.
        # Calculate center area of body.
        center_hips = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] + self.modeled_movement["LEFT_HIP_x"][self.pos]) / 2)
        if not inside_area_of_point("RIGHT_WRIST", center_hips, "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("inside"), "reference": _("center-of-body")} + ".", 2, "b1e4")

        # Exit : Right Wrist is above Nose.
        if above_of("RIGHT_WRIST", "NOSE", self.modeled_movement, self.pos):
            if self.debug:
                # Error: Right Wrist is away from Center of the Body.
                def draw_function(ax):
                    ax.axvline(x=center_hips * GlobalValues.frame_width, color='red', linestyle='--', alpha=0.7)
                    ax.axvline(x=(center_hips * GlobalValues.frame_width) + self.distance_threshold*GlobalValues.frame_width, color='red', linestyle='--', alpha=0.7)
                    ax.axvline(x=(center_hips * GlobalValues.frame_width) - self.distance_threshold*GlobalValues.frame_width, color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_HIP", "LEFT_HIP"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3.Transition 2 - Right Wrist is away from Center of the Body.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit : Right Wrist is above Nose.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["NOSE" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "NOSE"], self.modeled_movement_pixels, (self.finished_transition_1_pos, self.pos), self.output_path + "- 3.Transition 2 - Exit Right Wrist is above Nose.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

            self.change_rule()
            self.finished_transition_2 = True
            self.finished_transition_2_pos = self.pos

    def transition3(self):
        # Error: Right Wrist is not moving upward.
        if not goes_up("RIGHT_WRIST", self.modeled_movement, self.pos, 3):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "3"} + " - " + _("body-part-not-going-pos") % {"body_part": _("wrist"), "pos": _("up")} + ".", 1)

        # Error: Right Wrist is not above Right Elbow.
        if not above_of("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "3"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("elbow")} + ".", 1)

        # Exit : Right Wrist and Right Elbow stopped moving upward.
        if not goes_up("RIGHT_WRIST", self.modeled_movement, self.pos, 1) or \
           not goes_up("RIGHT_ELBOW", self.modeled_movement, self.pos, 1):
            if self.debug:
                # Error: Right Wrist is not above Right Elbow.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["RIGHT_ELBOW" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_ELBOW"], self.modeled_movement_pixels, (self.finished_transition_2_pos, self.pos), self.output_path + "- 4.Transition 3 - Right Wrist is not above Right Elbow.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit : Right Wrist and Right Elbow stopped moving upward.
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_ELBOW"], self.modeled_movement_pixels, (self.finished_transition_2_pos, self.pos), self.output_path + "- 4.Transition 3 - Exit Right Wrist and Right Elbow stopped moving upward.mp4", GlobalValues.frame_width, GlobalValues.frame_height)

            self.change_rule()
            self.finished_transition_3 = True
            self.finished_transition_3_pos = self.pos

    def transition4(self):
        # Error: Right Wrist is not above Right Eye.
        if not above_of("RIGHT_WRIST", "RIGHT_EYE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "4"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("head")} + ".", 1)

        # Error: Right Wrist is not above Right Elbow.
        if not above_of("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "4"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("elbow")} + ".", 1)

        # Error: Right Elbow is not near Ear (within a threshold).
        if not inside_area("RIGHT_ELBOW", "RIGHT_EAR", "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors,  self.movement_name + ": " + _("transition-name") % {"name": "4"} + " - " + _("body-part-far-from-reference") % {"body_part": _("elbow"), "reference": _("ear")} + ".", 1)

        # Error: Right Wrist is not at right of Nose.
        if not at_right_of("RIGHT_WRIST", "NOSE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "4"} + " - " + _("body-part-not-crossing-reference") % {"body_part": _("wrist"), "reference": _("nose")} + ".", 1)

        # Error: Right Wrist is not at left of Left Shoulder.
        if not at_left_of("RIGHT_WRIST", "LEFT_SHOULDER", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "4"} + " - " + _("body-part-beyond-reference") % {"body_part": _("wrist"), "reference": _("shoulder")} + ".", 1)

        # # Error: Arm is not at 125 degrees (as seen from the front) (within a threshold).
        # if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 125, 25, self.modeled_movement, self.pos):
        #     store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "4"} + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "125"} + ".", 1)

        # Exit: The last frame is reached.
        if self.pos == len(self.modeled_movement.index) - 2:
            if self.debug:
                # Error: Right Wrist is not above Right Elbow.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["RIGHT_ELBOW" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_ELBOW"], self.modeled_movement_pixels, (self.finished_transition_3_pos, self.pos), self.output_path + "- 5.Transition 4 - Right Wrist is not above Right Elbow.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not above Right Eye.
                def draw_function(ax):
                    ax.axhline(y=self.modeled_movement_pixels["RIGHT_EYE" + "_y"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_EYE"], self.modeled_movement_pixels, (self.finished_transition_3_pos, self.pos), self.output_path + "- 5.Transition 4 - Right Wrist is not above Right Eye.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Elbow is far from Right Ear (within a threshold).
                def draw_function(ax):
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_EAR" + "_x"][self.pos], color='red', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_EAR" + "_x"][self.pos] + self.distance_threshold*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                    ax.axvline(x=self.modeled_movement_pixels["RIGHT_EAR" + "_x"][self.pos] - self.distance_threshold*GlobalValues.frame_width, color='blue', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_ELBOW", "RIGHT_EAR"], self.modeled_movement_pixels, (self.finished_transition_3_pos, self.pos), self.output_path + "- 5.Transition 4 - Right Elbow is far from Right Ear.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not at right of Nose.
                def draw_function(ax):
                    ax.axvline(x=self.modeled_movement_pixels["NOSE" + "_x"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "NOSE"], self.modeled_movement_pixels, (self.finished_transition_3_pos, self.pos), self.output_path + "- 5.Transition 4 - Right Wrist is not at right of Nose.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Error: Right Wrist is not at left of Left Shoulder.
                def draw_function(ax):
                    ax.axvline(x=self.modeled_movement_pixels["LEFT_SHOULDER" + "_x"][self.pos], color='red', linestyle='--', alpha=0.7)
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "LEFT_SHOULDER"], self.modeled_movement_pixels, (self.finished_transition_3_pos, self.pos), self.output_path + "- 5.Transition 4 - Right Wrist is not at left of Left Shoulder.mp4", GlobalValues.frame_width, GlobalValues.frame_height, draw_function)

                # Exit: The last frame is reached.
                self.model.overlay_scatter_on_video(self.video_path, ["RIGHT_WRIST", "RIGHT_ELBOW"], self.modeled_movement_pixels, (self.finished_transition_3_pos, self.pos), self.output_path + "- 5.Transition 4 - Exit The last frame is reached.mp4", GlobalValues.frame_width, GlobalValues.frame_height)

            self.change_rule()
            self.finished_transition_4 = True
            self.finished_transition_4_pos = self.pos

    def ending_pose(self):
        # Error: Right Wrist is not above Right Eye.
        if not above_of("RIGHT_WRIST", "RIGHT_EYE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("head")} + ".", 1)

        # Error: Right Wrist is not above Right Elbow.
        if not above_of("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("elbow")} + ".", 1)

        # Error: Right Elbow is not near Ear (within a threshold).
        if not inside_area("RIGHT_ELBOW", "RIGHT_EAR", "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-far-from-reference") % {"body_part": _("elbow"), "reference": _("ear")} + ".", 1)

        # Error: Right Wrist is not at right of Nose.
        if not at_right_of("RIGHT_WRIST", "NOSE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-crossing-reference") % {"body_part": _("wrist"), "reference": _("nose")} + ".", 2, "b1e5")

        # Error: Right Wrist is not at left of Left Shoulder.
        if not at_left_of("RIGHT_WRIST", "LEFT_SHOULDER", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-beyond-reference") % {"body_part": _("wrist"), "reference": _("shoulder")} + ".", 1)

        # # Error: Arm is not at 125 degrees (as seen from the front) (within a threshold).
        # if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 125, 25, self.modeled_movement, self.pos):
        #     store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "125"} + ".", 1)

        self.change_rule()
