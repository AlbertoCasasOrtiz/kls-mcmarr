from abc import ABC, abstractmethod


class ResponseMcmarr(ABC):

    @abstractmethod
    def generate_response(self, movement_finished, analyzed_movement_errors, movement, next_movement):
        pass

    @abstractmethod
    def deliver_response(self, generated_response):
        pass
