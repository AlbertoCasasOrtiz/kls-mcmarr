from abc import ABC, abstractmethod


class MovementAnalyzer(ABC):

    def __init__(self, modeled_movement, movement_name, pos=0):
        self.finished_analysis = False
        self.movement_completed = True
        self.pos = pos
        self.errors = []
        self.entered_in_front_of_body = False
        self.current_rule = 1
        self.modeled_movement = modeled_movement
        self.movement_name = movement_name
        pass

    def change_rule(self):
        self.current_rule = self.current_rule + 1

    @abstractmethod
    def apply_rules(self):
        pass

    @abstractmethod
    def initial_pose(self):
        pass

    @abstractmethod
    def transitions(self):
        pass

    @abstractmethod
    def ending_pose(self):
        pass
