from kls_mcmarr.mcmarr.analyze.MovementAnalyzer import MovementAnalyzer as _MovementAnalyzer
from kls_mcmarr.mcmarr.analyze.utils import *


# Current max error score: 11
class RearElbowBlockAnalyzer(_MovementAnalyzer):

    def __init__(self, modeled_movement=None, movement_name="", pos=0):
        super().__init__(modeled_movement, movement_name, pos)
        self.distance_threshold = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] + self.modeled_movement["LEFT_HIP_x"][self.pos]) / 4)

    def apply_rules(self):
        while not self.finished_analysis:
            if self.current_rule == 1:
                self.initial_pose()
            elif 2 <= self.current_rule <= 2:
                self.transitions()
            elif self.current_rule == 3 and self.pos == len(self.modeled_movement.index) - 1:
                self.ending_pose()
            else:
                pass
            self.pos = self.pos + 1
            if self.pos >= len(self.modeled_movement.index):
                self.finished_analysis = True

        return self.movement_completed, self.errors

    def transitions(self):
        if self.pos == len(self.modeled_movement) - 2:
            self.change_rule()

    def initial_pose(self):
        # Elbow and wrist in same horizontal line.
        if not inside_area("RIGHT_WRIST", "RIGHT_ELBOW", "y", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-parts-not-same-line") % {"body_part_1": _("wrist"), "body_part_2": _("elbow"), "line_type": _("horizontal")} + ".", 1)

        # Wrist at approximate threshold distance of the hip.
        shoulder_x = self.modeled_movement["RIGHT_SHOULDER_x"][self.pos]
        wrist_x = self.modeled_movement["RIGHT_WRIST_x"][self.pos]
        if not at_left_of("RIGHT_WRIST", "RIGHT_HIP", self.modeled_movement, self.pos) and not shoulder_x - self.distance_threshold - self.distance_threshold < wrist_x < shoulder_x - self.distance_threshold:
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-distance-body-part") % {"body_part_1": _("wrist"), "body_part_2": _("body"), "distance": _("one-punch")} + ".", 2)

        # The wrist, elbow, shoulder segment is at approximately 180 degrees.
        if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 180, 15, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "180"} + ".", 1)

        # Check initial pose, and let the user do the movement. This one is not monitored except for initial and ending pose.
        self.change_rule()

    def ending_pose(self):
        # Condition: The wrist is above the hip.
        if not above_of("RIGHT_WRIST", "RIGHT_HIP", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("hip")} + ".", 2)

        # Condition: The wrist is below the plexus.
        plexus_point = get_plexus_point(self.modeled_movement, self.pos)
        if not below_of_point("RIGHT_WRIST", plexus_point, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("below"), "reference": _("solar-plexus")} + ".", 2)

        # Condition: The wrist is not far from body.
        if not inside_area("RIGHT_WRIST", "RIGHT_HIP", "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-far-from-reference") % {"body_part": _("wrist"), "reference": _("body")} + ".", 2)

        # Condition: The elbow is in the same vertical line as the wrist.
        if not inside_area("RIGHT_ELBOW", "RIGHT_WRIST", "y", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-parts-not-same-line") % {"body_part_1": _("elbow"), "body_part_2": _("wrist"), "line_type": _("vertical")} + ".", 1)
