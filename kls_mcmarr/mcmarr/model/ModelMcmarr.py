from abc import ABC, abstractmethod


class ModelMcmarr(ABC):

    @abstractmethod
    def model_movement(self, captured_movement, uuid_name):
        pass
