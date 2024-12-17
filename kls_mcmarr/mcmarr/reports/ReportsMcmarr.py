from abc import ABC, abstractmethod


class ReportsMcmarr(ABC):
    def __init__(self):
        self.detected_errors = []

    @abstractmethod
    def generate_reports(self, output_path, uuid_name, detected_errors, wrong_questions):
        pass

    @abstractmethod
    def generate_summary_report(self, output_path, uuid_name, detected_errors, wrong_questions):
        pass

    @abstractmethod
    def deliver_reports(self, generated_reports):
        pass
