from kls_mcmarr.mcmarr.analyze.AnalyzeMcmarr import AnalyzeMcmarr as _Analyze
from kls_mcmarr.kls.analyze.blocking_set_analyzer.BlockingSetAnalyzer import BlockingSetAnalyzer


class Analyze(_Analyze):

    def __init__(self, output_path):
        self.output_path = output_path
        self.blocking_set_analyzer = BlockingSetAnalyzer()
        pass

    def analyze_movement(self, modeled_movement, expected_movement, num_iter, uuid_name):
        # Analyze movement.
        return self.blocking_set_analyzer.analyze_movement(modeled_movement, expected_movement, self.output_path, num_iter, uuid_name)
