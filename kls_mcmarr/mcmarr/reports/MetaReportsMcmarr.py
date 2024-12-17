from abc import ABC, abstractmethod


class MetaReportsMcmarr(ABC):
    def __init__(self):
        self.detected_errors = []

    @abstractmethod
    def generate_meta_reports(self, session_path):
        pass


