from abc import ABC, abstractmethod


class Capture(ABC):

    @abstractmethod
    def capture_movement(self):
        pass
