from kls_mcmarr.mcmarr.analyze.MovementAnalyzer import MovementAnalyzer as _MovementAnalyzer


class EmptyAnalyzer(_MovementAnalyzer):

    def __init__(self, modeled_movement=None, movement_name="", pos=0):
        super().__init__(modeled_movement, movement_name, pos)
        self.errors.append([_("movement-not-detected-or-defined") + ".", 3])

    def apply_rules(self):
        return self.finished_analysis, self.errors

    def transitions(self):
        pass

    def initial_pose(self):
        pass

    def ending_pose(self):
        pass
