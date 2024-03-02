from kls_mcmarr.mcmarr.analyze.MovementAnalyzer import MovementAnalyzer as _MovementAnalyzer
from kls_mcmarr.mcmarr.analyze.utils import *


# Current max error score: 16
class InnerBlockAnalyzer(_MovementAnalyzer):

    def __init__(self, modeled_movement, movement_name, pos=0):
        super().__init__(modeled_movement, movement_name, pos)
        self.finished_initial_position = False
        self.finished_transition_1 = False
        self.finished_transition_2 = False

        self.distance_threshold = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] + self.modeled_movement["LEFT_HIP_x"][self.pos]) / 4)

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
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("stage-not-finished") % {"stage_name": _("initial-position")} + ". " + _("body-part-never-moved-pos") % {"body_part": _("wrist"), "pos": _("down-and-away-from-center-body")} + ". " + _("ending-position-never-reached") + ".", 3)
            self.movement_completed = False
        elif not self.finished_transition_1:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "1"}} + ". " + _("body-part-never-pos-relative-to") % {"body_part": _("wrist"), "reference_part": _("horizontal-line-eyes"), "pos": _("down")} + ". " + _("ending-position-never-reached") + ".", 3)
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
        # Exit: The wrist goes down and away from the center of the body.
        if goes_down("RIGHT_WRIST", self.modeled_movement, self.pos, 1) and goes_right("RIGHT_WRIST", self.modeled_movement, self.pos, 1):
            self.change_rule()
            self.finished_initial_position = True
        else:
            # The wrist is above the head.
            if not above_of("RIGHT_WRIST", "RIGHT_EYE", self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("head")} + ".", 2)

            # The wrist is above the elbow.
            if not above_of("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("elbow")} + ".", 2)

            # The elbow is near the ear.
            if not inside_area("RIGHT_ELBOW", "RIGHT_EAR", "y", self.distance_threshold, self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-far-from-reference") % {"body_part": _("elbow"), "reference": _("ear")} + ".", 1)

            # The wrist is crossing the nose.
            if not at_right_of("RIGHT_WRIST", "NOSE", self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-crossing-reference") % {"body_part": _("wrist"), "reference": _("nose")} + ".", 1)

            # The wrist is not crossing the shoulder.
            if not at_left_of("RIGHT_WRIST", "LEFT_SHOULDER", self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-beyond-reference") % {"body_part": _("wrist"), "reference": _("shoulder")} + ".", 1)

            # The wrist, elbow, shoulder section is at approximately 135 degrees.
            if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 135, 15, self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "135"} + ".", 1)

    def transition1(self):
        # Exit: The wrist is under the horizontal of the eyes.
        if below_of("RIGHT_WRIST", "RIGHT_EYE", self.modeled_movement, self.pos):
            self.change_rule()
            self.finished_transition_1 = True
        else:
            # The wrist follows approximately a rectilinear trajectory.
            if not follows_line("RIGHT_WRIST", self.modeled_movement, self.pos, self.distance_threshold):
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-following-trajectory") % {"body_part":_("wrist"), "trajectory_type":_("rectilinear")} + ".", 1)

    def transition2(self):
        # Exit: The last frame is reached.
        if self.pos == len(self.modeled_movement.index) - 1:
            self.change_rule()
            self.finished_transition_2 = True
        else:
            # The wrist must be kept above the mouth.
            if not above_of("RIGHT_WRIST", "MOUTH_RIGHT", self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("mouth")} + ".", 2)

    def ending_pose(self):
        # The wrist must be kept above the mouth.
        if not above_of("RIGHT_WRIST", "MOUTH_RIGHT", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("mouth")} + ".", 2)

        # The wrist is in the line of the shoulder.
        if not inside_area("RIGHT_WRIST", "RIGHT_SHOULDER", "y", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-parts-not-same-line") % {"body_part_1": _("wrist"), "body_part_2": _("shoulder"), "line_type": _("vertical")} + ".", 1)

        # The elbow is in the center line of the body.
        # Calculate center area of body.
        center_hips = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] + self.modeled_movement["LEFT_HIP_x"][self.pos]) / 2)
        if not inside_area_of_point("RIGHT_WRIST", center_hips, "y", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("elbow"), "reference": _("center-of-body")} + ".", 1)

        # The wrist, elbow, shoulder section is at approximately 45 degrees.
        if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 45, 15, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "45"} + ".", 1)

        self.change_rule()
