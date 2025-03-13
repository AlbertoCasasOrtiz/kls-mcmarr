import ast
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
from kls_mcmarr.kls.cognitive.Cognitive import Cognitive
from kls_mcmarr.kls.reports.metareports import MetaReports


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
            'num_reps': 0,
            'max_num_reps': 3,
            'continue_session': True,
            'current_question': 0,
            'answers': []
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

    # @unittest.skip("Too long.")
    def test_start_mcmarr_session(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/example/1.upward_block.mp4",
                                             "assets/example/2.hammering_inward_block.mp4",
                                             "assets/example/3.extended_outward_block.mp4",
                                             "assets/example/4.downward_outward_block.mp4",
                                             "assets/example/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_1(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_1/1.upward_block.mp4",
                                             "assets/test_videos/video_1/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_1/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_1/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_1/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_2(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_2/1.upward_block.mp4",
                                             "assets/test_videos/video_2/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_2/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_2/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_2/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_3(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_3/1.upward_block.mp4",
                                             "assets/test_videos/video_3/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_3/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_3/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_3/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_4(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_4/1.upward_block.mp4",
                                             "assets/test_videos/video_4/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_4/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_4/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_4/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_5(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_5/1.upward_block.mp4",
                                             "assets/test_videos/video_5/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_5/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_5/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_5/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_6(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_6/1.upward_block.mp4",
                                             "assets/test_videos/video_6/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_6/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_6/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_6/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_7(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_7/1.upward_block.mp4",
                                             "assets/test_videos/video_7/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_7/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_7/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_7/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_8(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_8/1.upward_block.mp4",
                                             "assets/test_videos/video_8/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_8/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_8/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_8/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_9(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_9/1.upward_block.mp4",
                                             "assets/test_videos/video_9/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_9/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_9/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_9/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_10(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_10/1.upward_block.mp4",
                                             "assets/test_videos/video_10/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_10/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_10/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_10/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_11(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_11/1.upward_block.mp4",
                                             "assets/test_videos/video_11/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_11/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_11/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_11/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_12(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_12/1.upward_block.mp4",
                                             "assets/test_videos/video_12/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_12/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_12/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_12/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_13(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_13/1.upward_block.mp4",
                                             "assets/test_videos/video_13/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_13/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_13/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_13/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_14(self):
        username = "username"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_14/1.upward_block.mp4",
                                             "assets/test_videos/video_14/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_14/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_14/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_14/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
        self.mcmarr.start_mcmarr_session("assets/output/capture/" + username + "/", username)

    @unittest.skip("Too long.")
    def test_video_15(self):
        username = "test-beginner"
        indications = Indications()
        capture = Capture(capture_mode="video",
                          input_video_paths=["assets/test_videos/video_15/1.upward_block.mp4",
                                             "assets/test_videos/video_15/2.hammering_inward_block.mp4",
                                             "assets/test_videos/video_15/3.extended_outward_block.mp4",
                                             "assets/test_videos/video_15/4.downward_outward_block.mp4",
                                             "assets/test_videos/video_15/5.rear_elbow_block.mp4"],
                          output_path="assets/output/capture/" + username + "/",
                          formats_to_store=['csv', 'json'])
        model = Model(generate_plots=True, output_path="assets/output/capture/" + username + "/")
        analyze = Analyze(output_path="assets/output/capture/" + username + "/")
        response = Response()
        reports = Reports()
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.current_movement = 0

        self.mcmarr.assign_phase_implementations(indications=indications,
                                                 capture=capture,
                                                 model=model,
                                                 analyze=analyze,
                                                 response=response,
                                                 reports=reports,
                                                 cognitive=cognitive,
                                                 metareports=metareports)

        self.mcmarr.load_set_of_movements("assets/sets/Set de Bloqueos I.xml")

        self.mcmarr.not_testing = True

        # Call the method to test
        self.mcmarr.current_movement = 0
        self.mcmarr.num_iter = 0
        self.mcmarr.continue_session = True
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
        cognitive = Cognitive()
        metareports = MetaReports()

        self.mcmarr.assign_phase_implementations(
            indications, capture, model, analyze, response, reports, cognitive, metareports)

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

    def test_metareport(self):
        username = "username"
        metareport = MetaReports()
        metareport.generate_meta_reports("assets/output/capture/" + username + "/")

    @unittest.skip("Too long.")
    def test_generate_report(self):
        output_path = ''

        if not output_path.endswith("/"):
            output_path = output_path + "/"

        kls = KLS()
        kls.reports = Reports()

        # Load compiled errors.
        for filename in os.listdir(output_path):
            if filename.endswith("-errors.txt"):
                parts = filename.split("-")
                iteration_number = parts[0]
                movement_name = parts[1]

                errors_list = []
                with open(output_path + filename, 'r') as file:
                    for line in file:
                        # Convert each line (which is a string representation of a list) into an actual list
                        individual_error = ast.literal_eval(
                            line.strip())  # Use strip() to remove any extra spaces/newlines
                        errors_list.append(individual_error)
                kls.compiled_errors.append([iteration_number, movement_name, errors_list])

        # Load wrong questions.
        for filename in os.listdir(output_path):
            if filename.endswith("-cognitive.txt"):
                with open(output_path + filename, 'r') as file:
                    for line in file:
                        individual_error = ast.literal_eval(line.strip())
                        correct = individual_error[0]
                        question = individual_error[1]
                        answer = individual_error[2]
                        question_id = individual_error[3]
                        kls.answers.append(
                            {"correct": correct, "question": question, "answer": answer, "id": question_id})

        generated_reports = kls.reports.generate_reports(output_path, "",
                                                         kls.compiled_errors, kls.answers, True)
        generated_reports = kls.reports.generate_summary_report(output_path, "",
                                                                kls.compiled_errors, kls.answers, True)

    def test_get_metareport_values(self):
        metareport = MetaReports()
        values = metareport.get_metareport_values("assets/output/capture/" + "username" + "/")
        print(values)

if __name__ == '__main__':
    unittest.main()
