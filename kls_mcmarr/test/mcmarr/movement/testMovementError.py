import unittest

from kls_mcmarr.mcmarr.movement.MovementError import MovementError


class TestMovementError(unittest.TestCase):

    def setUp(self):
        self.sample_data = {
            'name': 'ErrorName',
            'description': 'ErrorDescription',
            'feedback_message': 'ErrorFeedback',
            'start_frame': 10,
            'end_frame': 20,
            'keypoints': ['keypoint1', 'keypoint2']
        }
        self.movement_error = MovementError.from_dict(self.sample_data)

    def test_from_dict(self):
        from_dict = MovementError.from_dict(self.sample_data)

        self.assertEqual(from_dict.to_dict(), self.movement_error.to_dict())

    def test_from_json(self):
        json_str = '{"name": "ErrorName", "description": "ErrorDescription", "feedback_message": "ErrorFeedback", ' \
                   '"start_frame": 10, "end_frame": 20, "keypoints": ["keypoint1", "keypoint2"]}'
        error = MovementError.from_json(json_str)

        self.assertEqual(error.get_name(), "ErrorName")
        self.assertEqual(error.get_description(), "ErrorDescription")
        self.assertEqual(error.get_feedback_message(), "ErrorFeedback")
        self.assertEqual(error.get_start_frame(), 10)
        self.assertEqual(error.get_end_frame(), 20)
        self.assertEqual(error.get_keypoints(), ["keypoint1", "keypoint2"])

    def test_to_dict(self):
        self.assertEqual(self.movement_error.to_dict(), self.sample_data)

    def test_to_json(self):
        self.movement_error = MovementError.from_dict(self.sample_data)
        self.assertEqual(self.movement_error.to_dict(), self.sample_data)
        json_str = self.movement_error.to_json()
        self.assertEqual(MovementError.from_json(json_str).to_dict(), self.sample_data)

    def test_set_get_name(self):
        self.movement_error.set_name('TestName')
        self.assertEqual(self.movement_error.get_name(), 'TestName')

    def test_set_get_description(self):
        self.movement_error.set_description('TestDescription')
        self.assertEqual(self.movement_error.get_description(), 'TestDescription')

    def test_set_get_feedback_message(self):
        self.movement_error.set_feedback_message('TestFeedback')
        self.assertEqual(self.movement_error.get_feedback_message(), 'TestFeedback')

    def test_set_get_start_frame(self):
        self.movement_error.set_start_frame(5)
        self.assertEqual(self.movement_error.get_start_frame(), 5)

    def test_set_get_end_frame(self):
        self.movement_error.set_end_frame(30)
        self.assertEqual(self.movement_error.get_end_frame(), 30)

    def test_add_remove_keypoint(self):
        self.movement_error.add_keypoint('keypoint3')
        self.assertIn('keypoint3', self.movement_error.get_keypoints())
        self.assertTrue(self.movement_error.remove_keypoint('keypoint2'))
        self.assertNotIn('keypoint2', self.movement_error.get_keypoints())
        self.assertFalse(self.movement_error.remove_keypoint('keypoint2'))  # Try to remove a nonexistent keypoint

    def test_add_get_keypoint(self):
        self.movement_error.add_keypoint('keypoint1')
        self.assertEqual(self.movement_error.get_keypoint('keypoint1'), 'keypoint1')
        self.assertIsNone(self.movement_error.get_keypoint('nonexistent_keypoint'))

    def test_get_keypoint_names(self):
        self.assertEqual(self.movement_error.get_keypoint_names(), ['keypoint1', 'keypoint2'])


if __name__ == '__main__':
    unittest.main()
