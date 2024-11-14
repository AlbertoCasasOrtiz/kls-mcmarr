from kls_mcmarr.mcmarr.mcmarr import MCMARR


class KLS(MCMARR):

    def __init__(self):
        super().__init__()

    @classmethod
    def from_dict(cls, data):
        return super().from_dict(data)

    @classmethod
    def from_json(cls, data):
        return super().from_json(data)

    def to_dict(self):
        return super().to_dict()

    def to_json(self):
        return super().to_json()

    def start_mcmarr_session(self, output_path, uuid_user):
        super().start_mcmarr_session(output_path, uuid_user)

    def stop_mcmarr_session(self):
        super().stop_mcmarr_session()

    def condition_finish_session(self):
        return super().condition_finish_session()

    def assign_phase_implementations(self, indications, capture, model, analyze, response, reports, cognitive):
        super().assign_phase_implementations(indications, capture, model, analyze, response, reports, cognitive)

    def load_set_of_movements(self, path=None, string=None):
        super().load_set_of_movements(path, string)

    def set_set_of_movements(self, set_of_movements):
        super().set_set_of_movements(set_of_movements)

    def get_set_of_movements(self):
        return super().get_set_of_movements()

    def initialize_set(self):
        super().initialize_set()

    def get_current_movement(self):
        return super().get_current_movement()

    def get_next_movement(self):
        return super().get_next_movement()
