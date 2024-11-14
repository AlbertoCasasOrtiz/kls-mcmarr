from abc import ABC, abstractmethod


class CaptureMcmarr(ABC):

    @abstractmethod
    def capture_movement(self):
        pass
