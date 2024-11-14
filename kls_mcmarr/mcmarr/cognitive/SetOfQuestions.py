import json
from kls_mcmarr.mcmarr.cognitive.question.Question import Question


class SetOfQuestions:

    def __init__(self):
        # Information about the questions
        self.questions = []

    @classmethod
    def from_dict(cls, data):
        set_of_questions = cls()
        if 'questions' in data:
            set_of_questions.questions = [Question.from_dict(question) for question in data['questions']]
        return set_of_questions

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self):
        dict_set = {}
        if self.questions:
            dict_set['questions'] = [question.to_dict() for question in self.questions]
        return dict_set

    def to_json(self):
        return json.dumps(self.to_dict())

    def get_questions(self):
        return self.questions

    def set_questions(self, questions):
        self.questions = questions

    def get_question(self, pos):
        return self.questions[pos]

    def add_question(self, question):
        self.questions.append(question)

    def get_answers_question(self, pos):
        return self.get_question(pos).get_answers()

    def get_correct_answer_question(self, pos):
        return self.get_question(pos).get_correct_answer()

    def get_correct_answer_pos_question(self, pos):
        return self.get_question(pos).get_correct_answer_pos()
