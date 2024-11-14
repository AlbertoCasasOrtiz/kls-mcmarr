from abc import ABC, abstractmethod


class IndicationsMcmarr(ABC):

    @abstractmethod
    def generate_indications(self, movement_name):
        pass

    @abstractmethod
    def deliver_indications(self, indications):
        pass
