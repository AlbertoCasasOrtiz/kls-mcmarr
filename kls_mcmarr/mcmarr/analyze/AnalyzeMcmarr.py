from abc import ABC, abstractmethod


class AnalyzeMcmarr(ABC):

    @abstractmethod
    def analyze_movement(self, modeled_movement, expected_movement, num_iter, uuid_name):
        pass
