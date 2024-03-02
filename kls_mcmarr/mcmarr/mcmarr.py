import os
from datetime import datetime
import json

from abc import ABC, abstractmethod

from kls_mcmarr.mcmarr.movement.XmlSetLoader import XmlSetLoader
from kls_mcmarr.mcmarr.movement.SetOfMovements import SetOfMovements

# Initialize translations. Change language here if necessary.
import gettext
dir_path = os.path.dirname(os.path.realpath(__file__))
en = gettext.translation('messages', localedir=dir_path + "/" + '../locales', languages=['es'])
en.install()
_ = en.gettext


class MCMARR(ABC):

    def __init__(self):
        self.indications = None
        self.capture = None
        self.model = None
        self.analyze = None
        self.response = None
        self.reports = None

        self.set_of_movements = None
        self.current_movement = -1
        self.num_iter = 0

        self.continue_session = True

        self.not_testing = True

        self.compiled_errors = []

    @classmethod
    def from_dict(cls, data):
        mcmarr = cls()
        mcmarr.current_movement = data['current_movement']
        mcmarr.num_iter = data['num_iter']
        mcmarr.continue_session = data['continue_session']
        if 'compiled_errors' in data:
            mcmarr.compiled_errors = data['compiled_errors']
        if 'set_of_movements' in data:
            mcmarr.set_of_movements = SetOfMovements.from_dict(data['set_of_movements'])

        return mcmarr

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self):
        dict_mcmarr = {
            'current_movement': self.current_movement,
            'num_iter': self.num_iter,
            'continue_session': self.continue_session
        }
        if self.compiled_errors:
            dict_mcmarr['compiled_errors'] = self.compiled_errors
        if self.set_of_movements:
            dict_mcmarr['set_of_movements'] = self.set_of_movements.to_dict()
        return dict_mcmarr

    def to_json(self):
        return json.dumps(self.to_dict())

    @abstractmethod
    def start_mcmarr_session(self, output_path, user_uuid):
        # Iteration counter.
        self.num_iter = 0

        # Generate uuid_name to identify this session.
        current_datetime = datetime.now()
        ordered_string = current_datetime.strftime("%Y-%m-%d-%H-%M-%S")
        session_folder_name = "session - " + str(ordered_string) + "/"

        # Create session folder
        os.makedirs(output_path + session_folder_name)

        # Start mcmarr iteration.
        while self.condition_finish_session():

            # Get expected movement in this iteration.
            expected_movement = self.set_of_movements.get_movements()[self.current_movement]
            if self.current_movement + 1 < len(self.set_of_movements.get_movements()):
                next_movement = self.set_of_movements.get_movements()[self.current_movement + 1]
            else:
                next_movement = None

            # Iteration name.
            iteration_name = str(self.num_iter) + "-" + expected_movement.get_name()

            #    Provide indications about what to do.
            indications = self.indications.generate_indications(expected_movement.get_name())
            self.indications.deliver_indications(indications)

            # Log.
            print(f'Iteration {self.num_iter} started.')
            print("Indications: " + indications)

            #    Capture movement executed by learner.
            captured_movement = self.capture.capture_movement(self.current_movement, session_folder_name + iteration_name)
            #    Model captured movement.
            modeled_movement = self.model.model_movement(captured_movement, session_folder_name + iteration_name)

            #    Analyze modeled movement.
            movement_finished, analyzed_movement_errors = self.analyze.analyze_movement(modeled_movement,
                                                                                        expected_movement,
                                                                                        self.num_iter,
                                                                                        session_folder_name + iteration_name)
            #    Generate response and deliver it.
            generated_response, is_correct = self.response.generate_response(movement_finished,
                                                                             analyzed_movement_errors,
                                                                             expected_movement,
                                                                             next_movement)
            self.response.deliver_response(generated_response)

            self.compiled_errors.append([self.num_iter, expected_movement.get_name(), analyzed_movement_errors])

            # Update next movement.
            if is_correct:
                self.current_movement = self.current_movement + 1

            # Log.
            print("Generated Response: " + generated_response)
            print(f'Iteration {self.num_iter} finished.')
            print()

            # New iteration.
            self.num_iter = self.num_iter + 1

        # Generate reports at the end and deliver them.
        generated_reports = self.reports.generate_reports(output_path + session_folder_name + "/", user_uuid, self.compiled_errors)
        self.reports.deliver_reports(generated_reports)

    @abstractmethod
    def stop_mcmarr_session(self):
        self.continue_session = True

    @abstractmethod
    def condition_finish_session(self):
        return self.not_testing and self.continue_session and (self.current_movement < len(self.set_of_movements.get_movements()))

    def assign_phase_implementations(self, indications, capture, model, analyze, response, reports):
        self.indications = indications
        self.capture = capture
        self.model = model
        self.analyze = analyze
        self.response = response
        self.reports = reports

    def load_set_of_movements(self, path=None, string=None):
        loader = XmlSetLoader(path=path, string=string)
        self.set_of_movements = loader.load_xml_set()

    def set_set_of_movements(self, set_of_movements):
        self.set_of_movements = set_of_movements

    def get_set_of_movements(self):
        return self.set_of_movements

    def initialize_set(self):
        self.current_movement = -1
        self.num_iter = 0
        self.continue_session = True

    def get_current_movement(self):
        if self.current_movement < len(self.set_of_movements.get_movements()):
            return self.set_of_movements.get_movements()[self.current_movement]
        else:
            return None

    def get_next_movement(self):
        if self.current_movement < len(self.set_of_movements.get_movements()) - 1:
            self.current_movement = self.current_movement + 1
            return self.set_of_movements.get_movements()[self.current_movement]
        else:
            return None
