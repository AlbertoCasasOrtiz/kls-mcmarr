from kls_mcmarr.kls.analyze.blocking_set_analyzer.UpwardBlockAnalyzer import UpwardBlockAnalyzer
from kls_mcmarr.kls.analyze.blocking_set_analyzer.HammeringInwardBlockAnalyzer import HammeringInwardBlockAnalyzer
from kls_mcmarr.kls.analyze.blocking_set_analyzer.ExtendedOutwardBlockAnalyzer import ExtendedOutwardBlockAnalyzer
from kls_mcmarr.kls.analyze.blocking_set_analyzer.DownwardOutwardBlockAnalyzer import DownwardOutwardBlockAnalyzer
from kls_mcmarr.kls.analyze.blocking_set_analyzer.RearElbowBlockAnalyzer import RearElbowBlockAnalyzer
from kls_mcmarr.kls.analyze.blocking_set_analyzer.EmptyAnalyzer import EmptyAnalyzer
from kls_mcmarr.mcmarr.analyze.utils import store_error


class BlockingSetAnalyzer:

    def __init__(self):
        pass

    @staticmethod
    def check_body_parts(modeled_movement):
        if "RIGHT_WRIST_x" in modeled_movement and \
           "RIGHT_WRIST_y" in modeled_movement and \
           "RIGHT_HIP_x" in modeled_movement and \
           "RIGHT_HIP_y" in modeled_movement and\
           "RIGHT_ELBOW_x" in modeled_movement and \
           "RIGHT_ELBOW_y" in modeled_movement and \
           "RIGHT_SHOULDER_x" in modeled_movement and \
           "RIGHT_SHOULDER_y" in modeled_movement and \
           "LEFT_HIP_x" in modeled_movement and \
           "LEFT_HIP_y" in modeled_movement and \
           "LEFT_SHOULDER_x" in modeled_movement and \
           "LEFT_SHOULDER_y" in modeled_movement:
            body_parts_ok = True
        else:
            body_parts_ok = False

        return body_parts_ok

    def analyze_movement(self, modeled_movement, expected_movement, output_path, num_iter, uuid_name):
        # If all required body parts have not been detected, show error.
        if not self.check_body_parts(modeled_movement):
            analyzer = EmptyAnalyzer()
            analyzer.errors.clear()
            analyzer.finished_analysis = False
            store_error(analyzer.errors, _("required-body-parts-not-detected"), 3)
        # If all required body parts have been detected, proceed.
        else:
            # If we expect a movement, check its name and process it.
            if expected_movement is not None:
                if expected_movement.get_name() == "Upward Block" or expected_movement.get_name() == "Bloqueo Hacia Arriba":
                    analyzer = UpwardBlockAnalyzer(modeled_movement, expected_movement.get_name(), 0, False, video_path=output_path + uuid_name + "_raw.webm", output_path=output_path + uuid_name)
                    analyzer.apply_rules()
                elif expected_movement.get_name() == "Hammering Inward Block" or expected_movement.get_name() == "Bloqueo Hacia Adentro":
                    analyzer = HammeringInwardBlockAnalyzer(modeled_movement, expected_movement.get_name(), 0, False, video_path=output_path + uuid_name + "_raw.webm", output_path=output_path + uuid_name)
                    analyzer.apply_rules()
                elif expected_movement.get_name() == "Extended Outward Block" or expected_movement.get_name() == "Bloqueo Hacia Afuera Extendido":
                    analyzer = ExtendedOutwardBlockAnalyzer(modeled_movement, expected_movement.get_name(), 0, False, video_path=output_path + uuid_name + "_raw.webm", output_path=output_path + uuid_name)
                    analyzer.apply_rules()
                elif expected_movement.get_name() == "Downward Outward Block" or expected_movement.get_name() == "Bloqueo Hacia Abajo Hacia Fuera":
                    analyzer = DownwardOutwardBlockAnalyzer(modeled_movement, expected_movement.get_name(), 0, False, video_path=output_path + uuid_name + "_raw.webm", output_path=output_path + uuid_name)
                    analyzer.apply_rules()
                elif expected_movement.get_name() == "Rear Elbow Block" or expected_movement.get_name() == "Amartillamiento":
                    analyzer = RearElbowBlockAnalyzer(modeled_movement, expected_movement.get_name(), 0, False)
                    analyzer.apply_rules()
                # If we do not recognize the movement name, return unrecognized movement error.
                else:
                    analyzer = EmptyAnalyzer()
            # If we do not expect a movement, return unrecognized movement error.
            else:
                analyzer = EmptyAnalyzer()

        file = open(output_path + uuid_name + "-errors.txt", 'w')
        for error in analyzer.errors:
            file.write(str(error) + "\n")
        file.close()

        return analyzer.movement_completed, analyzer.errors
