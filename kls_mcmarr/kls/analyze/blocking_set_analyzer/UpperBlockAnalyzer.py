from kls_mcmarr.mcmarr.analyze.MovementAnalyzer import MovementAnalyzer as _MovementAnalyzer
from kls_mcmarr.mcmarr.analyze.utils import *

# Current max error score: 30
class UpperBlockAnalyzer(_MovementAnalyzer):

    def __init__(self, modeled_movement, movement_name, pos=0):
        super().__init__(modeled_movement, movement_name, pos)
        self.finished_initial_position = False
        self.finished_transition_1 = False
        self.finished_transition_2 = False
        self.finished_transition_3 = False
        self.finished_transition_4 = False

        self.distance_threshold = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] + self.modeled_movement["LEFT_HIP_x"][self.pos]) / 4)

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
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("stage-not-finished") % {"stage_name": _("initial-position")} + ". " + "The wrist never entered the body. Ending position was never reached.", 3)
            self.movement_completed = False
        elif not self.finished_transition_1:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "1"}} + ". " + _("body-part-never-pos-reference") % {"body_part":_("wrist"), "pos":_("above"), "reference":_("plexus") } + ". " + _("ending-position-never-reached") + ".", 3)
            self.movement_completed = False
        elif not self.finished_transition_2:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "1"}} + ". " + _("body-part-never-pos-reference") % {"body_part":_("wrist"), "pos":_("above"), "reference":_("nose") } + ". " + _("ending-position-never-reached") + ".", 3)
            self.movement_completed = False
        elif not self.finished_transition_3:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "3"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "3"}} + ". " + _("body-part-never-stopped-going-pos") % {"body_part":_("wrist"), "pos":_("up") } + ". " + _("ending-position-never-reached") + ".", 3)
            self.movement_completed = False
        elif not self.finished_transition_4:  # Should never happen, last frame should be always available.
            store_error(self.errors, self.movement_name + self.movement_name + ": " + _("transition-name") % {"name": "4"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "4"}} + ". " + _("error-reaching-last-frame") + ". ", 3)
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
        # Exit: The wrist enters the body (its at right of hip).
        if at_right_of("RIGHT_WRIST", "RIGHT_HIP", self.modeled_movement, self.pos):
            self.change_rule()
            self.finished_initial_position = True
        else:
            # Condition: The wrist is above the hip.
            if not above_of("RIGHT_WRIST", "RIGHT_HIP", self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("hip")} + ".", 2)

            # Condition: The wrist is below the plexus.
            plexus_point = get_plexus_point(self.modeled_movement, self.pos)
            if not below_of_point("RIGHT_WRIST", plexus_point, self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("below"), "reference": _("solar-plexus")} + ".", 2)

            # Condition: The wrist is not far from body.
            if not inside_area("RIGHT_WRIST", "RIGHT_HIP", "x", self.distance_threshold, self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-far-from-reference") % {"body_part": _("wrist"), "reference": _("body")} + ".", 2)

            # Condition: The elbow is in the same vertical line as the wrist.
            if not inside_area("RIGHT_ELBOW", "RIGHT_WRIST", "y", self.distance_threshold, self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-parts-not-same-line") % {"body_part_1": _("elbow"), "body_part_2": _("wrist"), "line_type": _("vertical")} + ".", 1)

    def transition1(self):
        # Exit : The wrist is above the plexus.
        # Calculate plexus point
        plexus = get_plexus_point(self.modeled_movement, self.pos)[1]
        if inside_area_of_point("RIGHT_WRIST", plexus, "y", self.distance_threshold, self.modeled_movement, self.pos):
            self.change_rule()
            self.finished_transition_1 = True
        else:
            # Condition: The wrist goes up.
            if not goes_up("RIGHT_WRIST", self.modeled_movement, self.pos, 1):
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-going-pos") % {"body_part": _("wrist"), "pos": _("up")} + ".", 2)

            # Condition: The wrist is not going towards the center of the body.
            if not goes_right("RIGHT_WRIST", self.modeled_movement, self.pos, 1):
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - "  + _("body-part-not-going-pos") % {"body_part": _("wrist"), "pos": _("center-of-body")} + ".", 1)

    def transition2(self):

        # The wrist goes above the nose.
        if above_of("RIGHT_WRIST", "NOSE", self.modeled_movement, self.pos):
            self.change_rule()
            self.finished_transition_2 = True
        else:
            # The wrist goes up.
            if not goes_up("RIGHT_WRIST", self.modeled_movement, self.pos, 1):
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-going-pos") % {"body_part": _("wrist"), "pos": _("up")} + ".", 2)

            # The wrist stays in the center of the body.
            # Calculate center area of body.
            center_hips = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] + self.modeled_movement["LEFT_HIP_x"][self.pos]) / 2)
            if not inside_area_of_point("RIGHT_WRIST", center_hips, "x", self.distance_threshold, self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("inside"), "reference": _("center-of-body")} + ".", 1)

    def transition3(self):
        # Not going up anymore.
        if not goes_up("RIGHT_WRIST", self.modeled_movement, self.pos, 1) or \
           not goes_up("RIGHT_ELBOW", self.modeled_movement, self.pos, 1):
            self.change_rule()
            self.finished_transition_3 = True
        else:
            # The wrist goes up.
            if not goes_up("RIGHT_WRIST", self.modeled_movement, self.pos, 1):
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "3"} + " - " + _("body-part-not-going-pos") % {"body_part": _("wrist"), "pos": _("up")} + ".", 2)

            # The wrist is above the elbow.
            if not above_of("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "3"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("elbow")} + ".", 2)

    def transition4(self):
        # Change rule when last pos is reached.
        if self.pos == len(self.modeled_movement.index) - 2:
            self.change_rule()
            self.finished_transition_4 = True
        else:
            # The wrist is above the nose.
            if not above_of("RIGHT_WRIST", "NOSE", self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "4"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("head")} + ".", 2)

            # The wrist is above the elbow.
            if not above_of("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "4"} + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("elbow")} + ".", 2)

            # The elbow is near the ear.
            if not inside_area("RIGHT_ELBOW", "RIGHT_EAR", "y", self.distance_threshold, self.modeled_movement, self.pos):
                store_error(self.errors,  self.movement_name + ": " + _("transition-name") % {"name": "3"} + " - " + _("body-part-far-from-reference") % {"body_part": _("elbow"), "reference": _("ear")} + ".", 1)

    def ending_pose(self):
        # The wrist is above the head.
        if not above_of("RIGHT_WRIST", "RIGHT_EYE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("head")} + ".", 2)

        # The wrist is above the elbow.
        if not above_of("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("elbow")} + ".", 2)

        # The elbow is near the ear.
        if not inside_area("RIGHT_ELBOW", "RIGHT_EAR", "y", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-far-from-reference") % {"body_part": _("elbow"), "reference": _("ear")} + ".", 1)

        # The wrist is crossing the nose.
        if not at_right_of("RIGHT_WRIST", "NOSE", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-crossing-reference") % {"body_part": _("wrist"), "reference": _("nose")} + ".", 1)

        # The wrist is not crossing the shoulder.
        if not at_left_of("RIGHT_WRIST", "LEFT_SHOULDER", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-beyond-reference") % {"body_part": _("wrist"), "reference": _("shoulder")} + ".", 1)

        # The wrist, elbow, shoulder section is at approximately 135 degrees.
        if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 135, 15, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "135"} + ".", 1)

        self.change_rule()
