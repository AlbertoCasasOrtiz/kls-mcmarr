import pandas as pd

from kls_mcmarr.mcmarr.analyze.MovementAnalyzer import MovementAnalyzer as _MovementAnalyzer
from kls_mcmarr.mcmarr.analyze.utils import *
from kls_mcmarr.kls.capture.global_values import GlobalValues
import matplotlib.pyplot as plt

# Current max error score: 16
class DownwardOutwardBlockAnalyzer(_MovementAnalyzer):

    def __init__(self, modeled_movement, movement_name, pos=0):
        super().__init__(modeled_movement, movement_name, pos)
        self.finished_initial_position = False
        self.finished_transition_1 = False
        self.finished_transition_2 = False

        self.start_transition_2 = 0

        self.center_elbow = None
        self.first_wrist_distance = None

        self.elbow_close_to_body = False

        self.distance_threshold = abs((self.modeled_movement["RIGHT_HIP_x"][self.pos] + self.modeled_movement["LEFT_HIP_x"][self.pos]) / 4)
        self.distance_threshold_pixels = self.distance_threshold * GlobalValues.frame_width

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
            store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("stage-not-finished") % {"stage_name": _("initial-position")} + ". " + _("body-part-never-moved-pos") % {"body_part": _("wrist"), "pos": _("right")} + ". " + _("ending-position-never-reached") + ".", 3)
            self.movement_completed = False
        elif not self.finished_transition_1:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "1"}} + ". " + _("body-part-never-moved-pos") % {"body_part": _("wrist"), "pos": _("down")} + ". " + _("ending-position-never-reached") + ".", 3)
            self.movement_completed = False
        elif not self.finished_transition_2:
            store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("stage-not-finished") % {"stage_name": _("transition-name") % {"name": "1"}} + ". " + _("error-reaching-last-frame") + ". " + _("ending-position-never-reached") + ".", 3)
            self.movement_completed = False

        return self.movement_completed, self.errors

    def transitions(self):
        if self.current_rule == 2:
            self.transition1()
        elif self.current_rule == 3:
            self.transition2()

    def initial_pose(self):
        # The wrist starts going right.
        if goes_right("RIGHT_WRIST", self.modeled_movement, self.pos, 1):
            self.change_rule()
            self.finished_initial_position = True
        else:
            # The wrist must be kept above the mouth.
            if not above_of("RIGHT_WRIST", "MOUTH_RIGHT", self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("wrist"), "pos": _("above"), "reference": _("mouth")} + ".", 2)

            # The wrist is at left of elbow.
            if not at_left_of("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-pos-reference") % {"body_part": _("arm"), "pos": _("at-left"), "reference": _("elbow")} + ".", 2)

            # The elbow forms a 90 degrees angle between wrist and shoulder.
            if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 90, 15, self.modeled_movement, self.pos):
                store_error(self.errors, self.movement_name + ": " + _("initial-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "90"} + ".", 1)

    def transition1(self):
        # Exit: The wrist starts going down.
        if goes_down("RIGHT_WRIST", self.modeled_movement, self.pos, 1):
            self.change_rule()
            self.start_transition_2 = self.pos
            self.finished_transition_1 = True
        else:
            # The wrist goes right.
            if not goes_right("RIGHT_WRIST", self.modeled_movement, self.pos, 3):
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-going-pos") % {"body_part": _("wrist"), "pos": _("right")} + ".", 2)

            # The elbow goes right.
            if not goes_right("RIGHT_ELBOW", self.modeled_movement, self.pos, 3):
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "1"} + " - " + _("body-part-not-going-pos") % {"body_part": _("elbow"), "pos": _("right")} + ".", 1)

    def transition2(self):
        # Exit: The last frame is reached.
        if self.pos == len(self.modeled_movement.index) - 1:

            # Check here if the elbow was at some point anchored to the body.
            if not self.elbow_close_to_body:
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-anchored") % {"body_part": _("elbow")} + ".", 1)

            self.change_rule()
            self.finished_transition_2 = True
        else:
            # First, lets calculate center of elbow.
            if self.center_elbow is None:
                elbow_points = []
                for i in range(self.start_transition_2, len(self.modeled_movement.index)):
                    elbow_points.append([self.modeled_movement["RIGHT_ELBOW_x"][i], self.modeled_movement["RIGHT_ELBOW_y"][i]])
                self.center_elbow = calculate_center(elbow_points)
                print(self.center_elbow)

            # Now, lets calculate wrist distance from wrist to center of elbow.
            if self.first_wrist_distance is None:
                # Needs to be converted to pixels to avoid deformation of resizing to values between 0 and 1.
                first_wrist_position = [self.modeled_movement["RIGHT_WRIST_x"][self.start_transition_2] * GlobalValues.frame_width,
                                        self.modeled_movement["RIGHT_WRIST_y"][self.start_transition_2] * GlobalValues.frame_height]
                center_elbow_pixels = [self.center_elbow[0] * GlobalValues.frame_width,
                                       self.center_elbow[1] * GlobalValues.frame_height]
                self.first_wrist_distance = math.dist(center_elbow_pixels, first_wrist_position)

            # The wrist follows a clockwise trajectory. We check the positions are not too close to each other to avoid accounting small variations at the end of the movement.
            if self.pos != len(self.modeled_movement.index) - 1 and abs(self.modeled_movement["RIGHT_WRIST_x"][self.pos] - self.modeled_movement["RIGHT_WRIST_x"][self.pos-1]) > self.modeled_movement["RIGHT_WRIST_x"].diff().mean():
                clockwise = follows_circular_clockwise_trajectory("RIGHT_WRIST", "RIGHT_ELBOW", self.modeled_movement, self.pos)
                if clockwise is not None and not clockwise:
                    store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-following-trajectory") % {"body_part": _("wrist"), "trajectory_type": _("clockwise")} + ".", 2)

            # The wrist follows a circular trajectory.
            # Needs to be converted to pixels to avoid deformation of resizing to values between 0 and 1.
            current_wrist_position = [self.modeled_movement["RIGHT_WRIST_x"][self.pos] * GlobalValues.frame_width,
                                      self.modeled_movement["RIGHT_WRIST_y"][self.pos] * GlobalValues.frame_height]
            center_elbow_pixels = [self.center_elbow[0] * GlobalValues.frame_width,
                                   self.center_elbow[1] * GlobalValues.frame_height]
            current_wrist_distance = math.dist(current_wrist_position, center_elbow_pixels)
            if abs(self.first_wrist_distance - current_wrist_distance) > self.distance_threshold_pixels:
                store_error(self.errors, self.movement_name + ": " + _("transition-name") % {"name": "2"} + " - " + _("body-part-not-following-trajectory") % {"body_part": _("wrist"), "trajectory_type": _("circular")} + ".", 2)

            # At some point, the elbow is close to the body. Checked in last frame.
            if inside_area("RIGHT_ELBOW", "RIGHT_HIP", "y", self.distance_threshold, self.modeled_movement, self.pos):
                self.elbow_close_to_body = True

    def ending_pose(self):
        # Elbow and wrist in same horizontal line.
        if not inside_area("RIGHT_WRIST", "RIGHT_ELBOW", "y", self.distance_threshold, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-parts-not-same-line") % {"body_part_1": _("wrist"), "body_part_2": _("elbow"), "line_type": _("horizontal")} + ".", 1)

        # Wrist at approximate threshold distance of the hip.
        shoulder_x = self.modeled_movement["RIGHT_SHOULDER_x"][self.pos]
        wrist_x = self.modeled_movement["RIGHT_WRIST_x"][self.pos]
        if not at_left_of("RIGHT_WRIST", "RIGHT_HIP", self.modeled_movement, self.pos) and not shoulder_x - self.distance_threshold - self.distance_threshold < wrist_x < shoulder_x - self.distance_threshold:
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-distance-body-part") % {"body_part_1": _("wrist"), "body_part_2": _("body"), "distance": _("one-punch")} + ".", 2)

        # The wrist, elbow, shoulder segment is at approximately 180 degrees.
        if not is_at_angle("RIGHT_WRIST", "RIGHT_ELBOW", "RIGHT_SHOULDER", 180, 15, self.modeled_movement, self.pos):
            store_error(self.errors, self.movement_name + ": " + _("ending-position") + " - " + _("body-part-not-at-angle") % {"body_part": _("arm"), "angle": "180"} + ".", 1)

        self.change_rule()
