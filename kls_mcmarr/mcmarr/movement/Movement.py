import json
from kls_mcmarr.mcmarr.movement.MovementError import MovementError


class Movement:

    def __init__(self):
        # Information about this movement.
        self.name = ""
        self.description = ""
        self.feedback_message = ""
        # Start and ending frame.
        self.start_frame = 0
        self.end_frame = 0
        # Order of the movement in the set.
        self.order = 0
        # List containing keypoints used in this movement.
        self.keypoints = []
        # List containing errors that can be committed while executing this movement.
        self.movement_errors = []

    @classmethod
    def from_dict(cls, data):
        movement = cls()
        movement.name = data['name']
        movement.description = data['description']
        movement.feedback_message = data['feedback_message']
        movement.start_frame = data['start_frame']
        movement.end_frame = data['end_frame']
        movement.order = data['order']
        movement.keypoints = data['keypoints']
        if 'movement_errors' in data:
            movement.movement_errors = [MovementError.from_dict(error_data) for error_data in data['movement_errors']]
        return movement

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self):
        dict_movement = {
            'name': self.name,
            'description': self.description,
            'feedback_message': self.feedback_message,
            'start_frame': self.start_frame,
            'end_frame': self.end_frame,
            'order': self.order,
            'keypoints': self.keypoints,
        }
        if self.movement_errors:
            dict_movement['movement_errors'] = [movement_error.to_dict() for movement_error in self.movement_errors]
        return dict_movement

    def to_json(self):
        return json.dumps(self.to_dict())

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_feedback_message(self):
        return self.feedback_message

    def set_feedback_message(self, feedback_message):
        self.feedback_message = feedback_message

    def get_start_frame(self):
        return self.start_frame

    def set_start_frame(self, start_frame):
        self.start_frame = start_frame

    def get_end_frame(self):
        return self.end_frame

    def set_end_frame(self, end_frame):
        self.end_frame = end_frame

    def get_order(self):
        return self.order

    def set_order(self, order):
        self.order = order

    def add_keypoint(self, keypoint):
        self.keypoints.append(keypoint)

    def remove_keypoint(self, keypoint):
        index = 0
        found = False
        for i in range(len(self.keypoints)):
            if keypoint == self.keypoints[i]:
                found = True
                index = i
                break
        if found:
            del self.keypoints[index]

    def get_keypoints(self):
        return self.keypoints

    def get_keypoint(self, name):
        res_keypoint = None
        for keypoint in self.keypoints:
            if name == keypoint:
                res_keypoint = keypoint
                break
        return res_keypoint

    def get_keypoint_names(self):
        names = []
        for keypoint in self.keypoints:
            names.append(keypoint)
        return names

    def add_movement_error(self, movement):
        self.movement_errors.append(movement)

    def remove_movement_error(self, name):
        index = 0
        found = False
        for i in range(len(self.movement_errors)):
            if name == self.movement_errors[i].name:
                found = True
                index = i
                break
        if found:
            del self.movement_errors[index]

    def get_movement_errors(self):
        return self.movement_errors

    def get_movement_error(self, name):
        res_movement = None
        for movement_error in self.movement_errors:
            if name == movement_error.name:
                res_movement = movement_error
                break
        return res_movement

    def get_movement_error_names(self):
        names = []
        for movement_error in self.movement_errors:
            names.append(movement_error.name)
        return names
