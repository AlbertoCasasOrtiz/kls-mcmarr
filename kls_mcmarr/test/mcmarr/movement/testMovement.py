import unittest

from kls_mcmarr.mcmarr.movement.Movement import Movement
from kls_mcmarr.mcmarr.movement.MovementError import MovementError


class TestMovement(unittest.TestCase):

    def setUp(self):
        self.sample_data = {
            'name': 'MovementName',
            'description': 'MovementDescription',
            'feedback_message': 'MovementFeedback',
            'start_frame': 10,
            'end_frame': 20,
            'order': 1,
            'keypoints': ['keypoint1', 'keypoint2'],
            'movement_errors': [
                {
                    'name': 'ErrorName1',
                    'description': 'ErrorDescription1',
                    'feedback_message': 'ErrorFeedback1',
                    'start_frame': 5,
                    'end_frame': 15,
                    'keypoints': ['keypoint1', 'keypoint2']
                },
                {
                    'name': 'ErrorName2',
                    'description': 'ErrorDescription2',
                    'feedback_message': 'ErrorFeedback2',
                    'start_frame': 15,
                    'end_frame': 25,
                    'keypoints': ['keypoint2', 'keypoint3']
                }
            ]
        }
        self.movement = Movement.from_dict(self.sample_data)

    def test_from_dict(self):
        from_dict = Movement.from_dict(self.sample_data)

        self.assertEqual(from_dict.to_dict(), self.movement.to_dict())

    def test_from_json(self):
        json_str = '{"name": "MovementName", "description": "MovementDescription", "feedback_message": \
                "MovementFeedback", "start_frame": 10, "end_frame": 20, "order": 1, "keypoints": ["keypoint1", \
                "keypoint2"], "movement_errors": [ { "name": "ErrorName1", "description": "ErrorDescription1", \
                "feedback_message": "ErrorFeedback1", "start_frame": 5, "end_frame": 15, "keypoints": ["keypoint1", \
                "keypoint2"] }, { "name": "ErrorName2", "description": "ErrorDescription2", "feedback_message": \
                "ErrorFeedback2", "start_frame": 15, "end_frame": 25, "keypoints": ["keypoint2", "keypoint3"] \
                } ] }'
        movement = Movement.from_json(json_str)

        self.assertEqual(movement.get_name(), "MovementName")
        self.assertEqual(movement.get_description(), "MovementDescription")
        self.assertEqual(movement.get_feedback_message(), "MovementFeedback")
        self.assertEqual(movement.get_start_frame(), 10)
        self.assertEqual(movement.get_end_frame(), 20)
        self.assertEqual(movement.get_order(), 1)
        self.assertEqual(movement.get_keypoints(), ["keypoint1", "keypoint2"])
        movement_errors = movement.get_movement_errors()

        self.assertEqual(movement_errors[0].get_name(), "ErrorName1")
        self.assertEqual(movement_errors[0].get_description(), "ErrorDescription1")
        self.assertEqual(movement_errors[0].get_feedback_message(), "ErrorFeedback1")
        self.assertEqual(movement_errors[0].get_start_frame(), 5)
        self.assertEqual(movement_errors[0].get_end_frame(), 15)
        self.assertEqual(movement_errors[0].get_keypoints(), ['keypoint1', 'keypoint2'])

        self.assertEqual(movement_errors[1].get_name(), "ErrorName2")
        self.assertEqual(movement_errors[1].get_description(), "ErrorDescription2")
        self.assertEqual(movement_errors[1].get_feedback_message(), "ErrorFeedback2")
        self.assertEqual(movement_errors[1].get_start_frame(), 15)
        self.assertEqual(movement_errors[1].get_end_frame(), 25)
        self.assertEqual(movement_errors[1].get_keypoints(), ['keypoint2', 'keypoint3'])

    def test_to_dict(self):
        self.assertEqual(self.movement.to_dict(), self.sample_data)

    def test_to_json(self):
        self.movement = Movement.from_dict(self.sample_data)
        self.assertEqual(self.movement.to_dict(), self.sample_data)
        json_str = self.movement.to_json()
        self.assertEqual(Movement.from_json(json_str).to_dict(), self.sample_data)

    def test_set_get_name(self):
        self.movement.set_name('TestName')
        self.assertEqual(self.movement.get_name(), 'TestName')

    def test_set_get_description(self):
        self.movement.set_description('TestDescription')
        self.assertEqual(self.movement.get_description(), 'TestDescription')

    def test_set_get_feedback_message(self):
        self.movement.set_feedback_message('TestFeedback')
        self.assertEqual(self.movement.get_feedback_message(), 'TestFeedback')

    def test_set_get_start_frame(self):
        self.movement.set_start_frame(5)
        self.assertEqual(self.movement.get_start_frame(), 5)

    def test_set_get_end_frame(self):
        self.movement.set_end_frame(30)
        self.assertEqual(self.movement.get_end_frame(), 30)

    def test_set_get_order(self):
        self.movement.set_order(2)
        self.assertEqual(self.movement.get_order(), 2)

    def test_add_remove_keypoint(self):
        self.movement.add_keypoint('keypoint3')
        self.assertIn('keypoint3', self.movement.get_keypoints())
        self.movement.remove_keypoint('keypoint2')
        self.assertNotIn('keypoint2', self.movement.get_keypoints())

    def test_get_keypoint(self):
        self.assertEqual(self.movement.get_keypoint('keypoint1'), 'keypoint1')
        self.assertIsNone(self.movement.get_keypoint('nonexistent_keypoint'))

    def test_get_keypoint_names(self):
        self.assertEqual(self.movement.get_keypoint_names(), ['keypoint1', 'keypoint2'])

    def test_add_remove_movement_error(self):
        error_data = {
            'name': 'ErrorName',
            'description': 'ErrorDescription',
            'feedback_message': 'ErrorFeedback',
            'start_frame': 5,
            'end_frame': 15,
            'keypoints': ['keypoint1', 'keypoint2']
        }
        movement_error = MovementError.from_dict(error_data)

        self.movement.add_movement_error(movement_error)
        self.assertIn(movement_error, self.movement.get_movement_errors())
        self.movement.remove_movement_error('ErrorName')
        self.assertNotIn(movement_error, self.movement.get_movement_errors())

    def test_get_movement_error(self):
        error_data = {
            'name': 'ErrorName',
            'description': 'ErrorDescription',
            'feedback_message': 'ErrorFeedback',
            'start_frame': 5,
            'end_frame': 15,
            'keypoints': ['keypoint1', 'keypoint2']
        }
        movement_error = MovementError.from_dict(error_data)
        self.movement.add_movement_error(movement_error)
        self.assertEqual(self.movement.get_movement_error('ErrorName1').get_name(), 'ErrorName1')
        self.assertIsNone(self.movement.get_movement_error('nonexistent_error'))

    def test_get_movement_error_names(self):
        error_names = [error['name'] for error in self.sample_data['movement_errors']]
        extracted_error_names = []
        for movement_error in self.movement.get_movement_errors():
            extracted_error_names.append(movement_error.get_name())

        self.assertEqual(self.movement.get_movement_error_names(), error_names)


if __name__ == '__main__':
    unittest.main()
