import json


class MovementError:

    def __init__(self):
        # Information about this incorrect movement.
        self.name = ""
        self.description = ""
        self.feedback_message = ""
        # Start and ending frame.
        self.start_frame = 0
        self.end_frame = 0
        # List containing keypoints used in this movement.
        self.keypoints = []

    @classmethod
    def from_dict(cls, data):
        movement_error = cls()
        movement_error.name = data['name']
        movement_error.description = data['description']
        movement_error.feedback_message = data['feedback_message']
        movement_error.start_frame = data['start_frame']
        movement_error.end_frame = data['end_frame']
        movement_error.keypoints = data['keypoints']
        return movement_error

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'feedback_message': self.feedback_message,
            'start_frame': self.start_frame,
            'end_frame': self.end_frame,
            'keypoints': self.keypoints
        }

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
            return True
        else:
            return False

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
