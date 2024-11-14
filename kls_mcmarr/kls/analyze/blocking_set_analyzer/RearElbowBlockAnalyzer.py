from kls_mcmarr.mcmarr.analyze.MovementAnalyzer import MovementAnalyzer as _MovementAnalyzer
from kls_mcmarr.mcmarr.analyze.utils import *

from kls_mcmarr.kls.model.model import Model

# Current max error score: 7
class RearElbowBlockAnalyzer(_MovementAnalyzer):

    def __init__(self, modeled_movement=None, movement_name="", pos=0, debug=False):
        super().__init__(modeled_movement, movement_name, pos)

        self.debug = debug

        self.distance_threshold = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] - self.modeled_movement["LEFT_HIP_x"][self.pos]) / 2)

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
        # Error: Right Wrist and Right Elbow are not in the same horizontal line.
        if not inside_area("RIGHT_WRIST", "RIGHT_ELBOW", "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-parts-not-same-line") % {"body_part_1": _("wrist"), "body_part_2": _("elbow"), "line_type": _("horizontal")} + ".", 1)

        # Error: Right Wrist is not at left of Right Hip (within a threshold).
        if not at_left_of("RIGHT_WRIST", "RIGHT_HIP", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-distance-body-part") % {"body_part_1": _("wrist"), "body_part_2": _("body"), "distance": _("one-punch")} + ".", 1)

        # Error: Right Wrist is not near Right Hip (within a threshold).
        if not inside_area("RIGHT_WRIST", "RIGHT_HIP", "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-far-from-reference") % {"body_part": _("wrist"), "reference": _("hip")} + ".", 1)

        # # Error: Arm is not at 180 degrees (as seen from the front) (within a threshold).
        # if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 180, 25, self.modeled_movement, self.pos):
        #     store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "180"} + ".", 1)

        if self.debug:
            model = Model(output_path="C:\\Users\\alber\\Desktop")
            model.print_scatter_plot(["RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_HIP", "NOSE", "RIGHT_EYE", "LEFT_SHOULDER"], self.modeled_movement, (0, self.pos), "5.Rear Elbow Block - 1.Initial Position", True)

        # Check initial pose, and let the user do the movement. This one is not monitored except for initial and ending pose.
        self.change_rule()

    def ending_pose(self):
        # Error: Right Wrist is not above Right Hip.
        if not above_of("RIGHT_WRIST", "RIGHT_HIP", self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("hip")} + ".", 1)

        # Error: Right Wrist is not below Solar Plexus.
        plexus_point = get_plexus_point(self.modeled_movement, self.pos)
        if not below_of_point("RIGHT_WRIST", plexus_point, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("below"), "reference": _("solar-plexus")} + ".", 1)

        # Error: Right Wrist is far from Right Hip (within a threshold).
        if not inside_area("RIGHT_WRIST", "RIGHT_HIP", "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-far-from-reference") % {"body_part": _("wrist"), "reference": _("body")} + ".", 1)

        # Error: Right Wrist and Right Elbow are not in the same vertical line (within a threshold).
        if not inside_area("RIGHT_ELBOW", "RIGHT_WRIST", "x", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-parts-not-same-line") % {"body_part_1": _("elbow"), "body_part_2": _("wrist"), "line_type": _("vertical")} + ".", 1)

        if self.debug:
            model = Model(output_path="C:\\Users\\alber\\Desktop")
            model.print_scatter_plot(["RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_HIP", "NOSE", "RIGHT_EYE", "LEFT_SHOULDER"], self.modeled_movement, (0, self.pos), "5.Rear Elbow Block - 1.Ending Pose", True)
