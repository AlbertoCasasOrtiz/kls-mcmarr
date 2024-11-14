import json
import pandas as pd

from kls_mcmarr.mcmarr.movement.Movement import Movement


class SetOfMovements:

    def __init__(self, model=None):
        # Information about the set.
        self.name = ""
        self.description = ""
        # Template from video of this set.
        self.template = None
        # List of movements contained in this set.
        self.movements = []
        # Implementation of class model to apply.
        self.model = model

    @classmethod
    def from_dict(cls, data):
        set_of_movements = cls()
        set_of_movements.name = data['name']
        set_of_movements.description = data['description']
        set_of_movements.template = data['template']
        if 'movements' in data:
            set_of_movements.movements = [Movement.from_dict(movement) for movement in data['movements']]
        return set_of_movements

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self):
        dict_set = {
            'name': self.name,
            'description': self.description,
            'template': self.template,
        }
        if self.movements:
            dict_set['movements'] = [movement.to_dict() for movement in self.movements]
        return dict_set

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

    def get_template(self):
        return self.template

    def set_template(self, json_template):
        # Store modeled template.
        self.template = json_template

    def add_movement(self, movement):
        self.movements.append(movement)

    def remove_movement(self, name):
        index = 0
        found = False
        for i in range(len(self.movements)):
            if name == self.movements[i].name:
                found = True
                index = i
                break
        if found:
            del self.movements[index]
            return True
        else:
            return False

    def remove_movement_error(self, name):
        for movement in self.movements:
            removed = movement.remove_movement_error(name)
            if removed:
                return True
        return False

    def get_movements(self):
        return self.movements

    def get_movement(self, name):
        res_movement = None
        for movement in self.movements:
            if name == movement.name:
                res_movement = movement
                break
        return res_movement

    def get_movement_names(self):
        names = []
        for movement in self.movements:
            names.append(movement.name)
        return names

    @staticmethod
    def template_json_to_df(json_template):
        if isinstance(json_template, str):
            json_template = json.loads(json_template)

        df_template = None
        if json_template:
            df_template = pd.DataFrame(columns=SetOfMovements.get_df_header())

            for attribute, value in json_template.items():
                row = []
                for landmark, coordinates in value.items():
                    row.append(coordinates['x'])
                    row.append(coordinates['y'])
                    row.append(coordinates['z'])
                    row.append(coordinates['visibility'])
                df_template.loc[len(df_template)] = row

        return df_template

    @staticmethod
    def get_df_header():
        mediapipe_landmarks = {"NOSE": 0,
                               "LEFT_EYE_INNER": 1,
                               "LEFT_EYE": 2,
                               "LEFT_EYE_OUTER": 3,
                               "RIGHT_EYE_INNER": 4,
                               "RIGHT_EYE": 5,
                               "RIGHT_EYE_OUTER": 6,
                               "LEFT_EAR": 7,
                               "RIGHT_EAR": 8,
                               "MOUTH_LEFT": 9,
                               "MOUTH_RIGHT": 10,
                               "LEFT_SHOULDER": 11,
                               "RIGHT_SHOULDER": 12,
                               "LEFT_ELBOW": 13,
                               "RIGHT_ELBOW": 14,
                               "LEFT_WRIST": 15,
                               "RIGHT_WRIST": 16,
                               "LEFT_PINKY": 17,
                               "RIGHT_PINKY": 18,
                               "LEFT_INDEX": 19,
                               "RIGHT_INDEX": 20,
                               "LEFT_THUMB": 21,
                               "RIGHT_THUMB": 22,
                               "LEFT_HIP": 23,
                               "RIGHT_HIP": 24,
                               "LEFT_KNEE": 25,
                               "RIGHT_KNEE": 26,
                               "LEFT_ANKLE": 27,
                               "RIGHT_ANKLE": 28,
                               "LEFT_HEEL": 29,
                               "RIGHT_HEEL": 30,
                               "LEFT_FOOT_INDEX": 31,
                               "RIGHT_FOOT_INDEX": 32}

        landmark_strings = mediapipe_landmarks.keys()

        header = []
        for string in landmark_strings:
            header.append(string + "_x")
            header.append(string + "_y")
            header.append(string + "_z")
            header.append(string + "_v")

        return header

    def get_template_of_movement(self, name):
        # Get full template.
        full_template = self.template_json_to_df(self.get_template())

        # Get movement and keypoints.
        movement = self.get_movement(name)

        if movement is not None:
            movement_keypoints = movement.get_keypoints()

            # Get keypoint per coordinate (and visibility).
            keypoints_coordinates = []
            for keypoints in movement_keypoints:
                keypoints_coordinates.append(keypoints + "_x")
                keypoints_coordinates.append(keypoints + "_y")
                keypoints_coordinates.append(keypoints + "_z")
                keypoints_coordinates.append(keypoints + "_v")

            # Get interval in which the movement is encapsulated.
            movement_interval = (movement.get_start_frame(), movement.get_end_frame())

            # Return template for this movement.
            if full_template:
                return full_template[keypoints_coordinates].loc[movement_interval[0]:movement_interval[1]]
            else:
                return None
        else:
            return None

    def set_model_implementation(self, model):
        self.model = model
