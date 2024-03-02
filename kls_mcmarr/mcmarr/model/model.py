from abc import ABC, abstractmethod


class Model(ABC):

    @abstractmethod
    def model_movement(self, captured_movement, uuid_name):
        pass
