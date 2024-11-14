import unittest
import json
import os
import pandas as pd

from kls_mcmarr.mcmarr.movement.Movement import Movement
from kls_mcmarr.mcmarr.movement.MovementError import MovementError
from kls_mcmarr.mcmarr.movement.SetOfMovements import SetOfMovements
from kls_mcmarr.mcmarr.movement.XmlSetLoader import XmlSetLoader
from kls_mcmarr.kls.model.model import Model


class TestSetOfMovements(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.chdir("../../")

    @classmethod
    def tearDownClass(cls):
        os.chdir("kls_mcmarr/test/")

    def setUp(self):
        loader = XmlSetLoader("assets/sets/Set de Bloqueos I.xml")
        self.set_of_movements = loader.load_xml_set()
        self.set_of_movements.set_model_implementation(Model(generate_plots=True, output_path="assets/output/capture/"))

    def test_from_dict(self):

        sample_data = {
            'name': self.set_of_movements.get_name(),
            'description': self.set_of_movements.get_description(),
            'template': self.set_of_movements.get_template(),
            'movements': [movement.to_dict() for movement in self.set_of_movements.get_movements()],
        }
        from_dict = SetOfMovements.from_dict(sample_data)

        self.assertEqual(from_dict.to_dict(), self.set_of_movements.to_dict())

    def test_from_json(self):
        json_str = '{"name": "This is a name", "description": "This is a description", "template": "This is a template",\
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
        set_of_movements = SetOfMovements.from_json(json_str)

        self.assertEqual(set_of_movements.get_name(), "This is a name")
        self.assertEqual(set_of_movements.get_description(), "This is a description")
        self.assertEqual(set_of_movements.get_template(), "This is a template")

        movements = set_of_movements.get_movements()

        self.assertEqual(movements[0].get_name(), "MovementName")
        self.assertEqual(movements[0].get_description(), "MovementDescription")
        self.assertEqual(movements[0].get_feedback_message(), "MovementFeedback")
        self.assertEqual(movements[0].get_start_frame(), 10)
        self.assertEqual(movements[0].get_end_frame(), 20)
        self.assertEqual(movements[0].get_order(), 1)
        self.assertEqual(movements[0].get_keypoints(), ['keypoint1', 'keypoint2'])
        movement_errors = movements[0].get_movement_errors()

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

        self.assertEqual(movements[1].get_name(), "MovementName2")
        self.assertEqual(movements[1].get_description(), "MovementDescription2")
        self.assertEqual(movements[1].get_feedback_message(), "MovementFeedback2")
        self.assertEqual(movements[1].get_start_frame(), 20)
        self.assertEqual(movements[1].get_end_frame(), 30)
        self.assertEqual(movements[1].get_order(), 2)
        self.assertEqual(movements[1].get_keypoints(), ['keypoint3', 'keypoint4'])
        movement_errors = movements[1].get_movement_errors()

        self.assertEqual(movement_errors[0].get_name(), "ErrorName3")
        self.assertEqual(movement_errors[0].get_description(), "ErrorDescription3")
        self.assertEqual(movement_errors[0].get_feedback_message(), "ErrorFeedback3")
        self.assertEqual(movement_errors[0].get_start_frame(), 15)
        self.assertEqual(movement_errors[0].get_end_frame(), 25)
        self.assertEqual(movement_errors[0].get_keypoints(), ['keypoint3', 'keypoint4'])

        self.assertEqual(movement_errors[1].get_name(), "ErrorName4")
        self.assertEqual(movement_errors[1].get_description(), "ErrorDescription4")
        self.assertEqual(movement_errors[1].get_feedback_message(), "ErrorFeedback4")
        self.assertEqual(movement_errors[1].get_start_frame(), 35)
        self.assertEqual(movement_errors[1].get_end_frame(), 45)
        self.assertEqual(movement_errors[1].get_keypoints(), ['keypoint4', 'keypoint5'])

    def test_to_dict(self):
        json_str = '{"name": "This is a name", "description": "This is a description", "template": "This is a template",\
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
        set_of_movements = SetOfMovements.from_json(json_str)
        dict = set_of_movements.to_dict()
        expected_dict = json.loads(json_str)

        self.assertEqual(dict, expected_dict)

    def test_to_json(self):
        json_str = '{"name": "This is a name", "description": "This is a description", "template": "This is a template",\
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
        set_of_movements = SetOfMovements.from_json(json_str)
        to_json = set_of_movements.to_json()
        json_orig = json.loads(json_str)
        self.assertEqual(SetOfMovements.from_json(to_json).to_dict(), json_orig)

    def test_set_get_name(self):
        self.set_of_movements.set_name('TestSet')
        self.assertEqual(self.set_of_movements.get_name(), 'TestSet')

    def test_set_get_description(self):
        self.set_of_movements.set_description('TestDescription')
        self.assertEqual(self.set_of_movements.get_description(), 'TestDescription')

    def test_set_get_template(self):
        self.set_of_movements.set_template(self.set_of_movements.get_template())
        self.assertNoLogs(self.set_of_movements.get_template())

    def test_add_remove_movement(self):
        # Create a sample movement
        movement = Movement()
        movement.set_name('Movement1')

        self.set_of_movements.add_movement(movement)
        self.assertIn('Movement1', self.set_of_movements.get_movement_names())

        self.set_of_movements.remove_movement('Movement1')
        self.assertNotIn('Movement1', self.set_of_movements.get_movement_names())

    def test_remove_movement_error(self):
        # Create a sample movement
        movement = Movement()
        movement.set_name('MovementTest')

        movement_error = MovementError()
        movement_error.set_name('MovementTestError1')

        movement.add_movement_error(movement_error)

        self.set_of_movements.add_movement(movement)

        self.assertIn(movement, self.set_of_movements.get_movements())
        self.assertIn(movement_error, movement.get_movement_errors())

        self.set_of_movements.remove_movement_error('MovementTestError1')
        self.assertNotIn(movement_error, movement.get_movement_errors())

    def test_get_movements(self):
        movement1 = Movement()
        movement2 = Movement()
        self.set_of_movements.movements = [movement1, movement2]

        movements = self.set_of_movements.get_movements()
        self.assertEqual(len(movements), 2)

    def test_get_movement(self):
        movement1 = Movement()
        movement2 = Movement()
        movement1.name = 'Movement1'
        movement2.name = 'Movement2'
        self.set_of_movements.movements = [movement1, movement2]

        found_movement = self.set_of_movements.get_movement('Movement1')
        self.assertEqual(found_movement.name, 'Movement1')

    def test_get_movement_names(self):
        movement1 = Movement()
        movement2 = Movement()
        movement1.name = 'Movement1'
        movement2.name = 'Movement2'
        self.set_of_movements.movements = [movement1, movement2]

        names = self.set_of_movements.get_movement_names()
        self.assertEqual(names, ['Movement1', 'Movement2'])

    def test_template_json_to_df(self):
        df = None
        if self.set_of_movements.get_template():
            json_template = json.loads(self.set_of_movements.get_template())
            df = self.set_of_movements.template_json_to_df(json_template)
        self.assertIsInstance(df, pd.DataFrame | None)

    def test_get_df_header(self):
        header = self.set_of_movements.get_df_header()
        self.assertIsInstance(header, list)

    def test_get_template_of_movement(self):
        template = self.set_of_movements.get_template_of_movement('Upper Block')
        self.assertIsInstance(template, pd.DataFrame | None)


if __name__ == '__main__':
    unittest.main()
