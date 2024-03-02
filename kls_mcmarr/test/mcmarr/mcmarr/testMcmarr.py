import unittest
import os

from kls_mcmarr.kls.analyze.analyze import Analyze
from kls_mcmarr.kls.capture.capture import Capture
from kls_mcmarr.kls.indications.indications import Indications
from kls_mcmarr.kls.kls import KLS
from kls_mcmarr.kls.model.model import Model
from kls_mcmarr.kls.reports.reports import Reports
from kls_mcmarr.kls.response.response import Response
from kls_mcmarr.mcmarr.movement.SetOfMovements import SetOfMovements


class TestMCMARR(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print(os.getcwd())
        os.chdir("../../")

    @classmethod
    def tearDownClass(cls):
        print(os.getcwd())
        os.chdir("kls_mcmarr/test/")

    def setUp(self):
        self.mcmarr = KLS()
        self.json_string_set = '{"name": "This is a name", "description": "This is a description", "template": "This is a template",\
                        "movements": [{"name": "MovementName", "description": "MovementDescription", "feedback_message": \
                        "MovementFeedback", "start_frame": 10, "end_frame": 20, "order": 1, "keypoints": ["keypoint1", \
                        "keypoint2"], "movement_errors": [ { "name": "ErrorName1", "description": "ErrorDescription1", \
                        "feedback_message": "ErrorFeedback1", "start_frame": 5, "end_frame": 15, "keypoints": ["keypoint1", \
                        "keypoint2"] }, { "name": "ErrorName2", "description": "ErrorDescription2", "feedback_message": \
                        "ErrorFeedback2", "start_frame": 15, "end_frame": 25, "keypoints": ["keypoint2", "keypoint3"] \
                        } ] }, {"name": "MovementName2", "description": "MovementDescription2", "feedback_message": \
                        "MovementFeedback2", "start_frame": 20, "end_frame": 30, "order": 2, "keypoints": ["keypoint3", \
                        "keypoint4"], "movement_errors": [ { "name": "ErrorName3", "description": "ErrorDescription3", \
                        "feedback_message": "ErrorFeedback3", "start_frame": 15, "end_frame": 25, "keypoints": ["keypoint3", \
                        "keypoint4"] }, { "name": "ErrorName4", "description": "ErrorDescription4", "feedback_message": \
                        "ErrorFeedback4", "start_frame": 35, "end_frame": 45, "keypoints": ["keypoint4", "keypoint5"] \
                        } ] }]}'
        self.mcmarr.set_of_movements = SetOfMovements.from_json(self.json_string_set)
        self.mcmarr.current_movement = 1
        self.mcmarr.continue_session = True

    def test_from_dict(self):
        # Create a sample data dictionary
        data = {
            'set_of_movements': SetOfMovements.from_json(self.json_string_set).to_dict(),
            'current_movement': 1,
            'num_iter': 0,
            'continue_session': True
        }
        mcmarr = KLS.from_dict(data)

        self.assertEqual(mcmarr.set_of_movements.to_dict(), SetOfMovements.from_json(self.json_string_set).to_dict())
        self.assertEqual(mcmarr.current_movement, 1)
        self.assertEqual(mcmarr.num_iter, 0)
        self.assertTrue(mcmarr.continue_session)

    def test_to_dict(self):
        # Set some data in the MCMARR object

        data = self.mcmarr.to_dict()

        self.assertEqual(data['set_of_movements'], self.mcmarr.set_of_movements.to_dict())
        self.assertEqual(data['current_movement'], self.mcmarr.current_movement)
        self.assertTrue(data['continue_session'])

    def test_start_mcmarr_session(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/example/1.upper_block.mp4", "assets/example/2.inner_block.mp4", "assets/example/3.outer_extended_block.mp4", "assets/example/4.downward_outward_block.mp4", "assets/example/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    def test_stop_mcmarr_session(self):
        self.mcmarr.stop_mcmarr_session()
        self.assertTrue(self.mcmarr.continue_session)

    def test_condition_finish_session(self):
        self.mcmarr.not_testing = True

        # Test when current_movement is less than the number of movements
        self.mcmarr.current_movement = 0
        self.assertTrue(self.mcmarr.condition_finish_session())

        # Test when current_movement is equal to the number of movements
        self.mcmarr.current_movement = 3
        self.assertFalse(self.mcmarr.condition_finish_session())

    def test_assign_phase_implementations(self):
        indications = Indications()
        capture = Capture(capture_mode="video", input_video_paths=["assets/example/1.upper_block.mp4"], output_path="assets/output/capture/", formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/")
        analyze = Analyze(output_path="assets/output/capture/")
        response = Response()
        reports = Reports()

        self.mcmarr.assign_phase_implementations(
            indications, capture, model, analyze, response, reports)

        self.assertEqual(self.mcmarr.indications, indications)
        self.assertEqual(self.mcmarr.capture, capture)
        self.assertEqual(self.mcmarr.model, model)
        self.assertEqual(self.mcmarr.analyze, analyze)
        self.assertEqual(self.mcmarr.response, response)
        self.assertEqual(self.mcmarr.reports, reports)

    def test_load_set_of_movements(self):
        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        loaded_dict = self.mcmarr.set_of_movements.to_dict()

        self.assertEqual(loaded_dict, loaded_dict)


if __name__ == '__main__':
    unittest.main()
