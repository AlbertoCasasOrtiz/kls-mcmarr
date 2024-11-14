from abc import ABC, abstractmethod


class AffectiveMcmarr(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_affective_status(self, image):
        pass
