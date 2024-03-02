from abc import ABC, abstractmethod


class Reports(ABC):
    def __init__(self):
        self.detected_errors = []

    @abstractmethod
    def generate_reports(self, output_path, uuid_name, detected_errors):
        pass

    @abstractmethod
    def deliver_reports(self, generated_reports):
        pass
