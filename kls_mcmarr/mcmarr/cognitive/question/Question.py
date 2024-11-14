import json


class Question:

    def __init__(self):
        # Information about the question.
        self.id = 0
        self.question = ""
        self.answers = []
        self.correct_answer_pos = 0

    @classmethod
    def from_dict(cls, data):
        question = cls()
        question.id = data['id']
        question.question = data['question']
        question.correct_answer_pos = data['correct_answer_pos']
        if 'answers' in data:
            question.answers = [answer for answer in data['answers']]
        return question

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self):
        dict_question = {
            'id': self.id,
            'question': self.question,
            'correct_answer_pos': self.correct_answer_pos,
        }
        if self.answers:
            dict_question['answers'] = [answer for answer in self.answers]
        return dict_question

    def to_json(self):
        return json.dumps(self.to_dict())

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_question(self):
        return self.question

    def set_question(self, question):
        self.question = question

    def get_correct_answer_pos(self):
        return self.correct_answer_pos

    def set_correct_answer_pos(self, correct_answer_pos):
        self.correct_answer_pos = correct_answer_pos

    def get_correct_answer(self):
        return self.answers[int(self.correct_answer_pos)]

    def get_answers(self):
        return self.answers

    def set_answers(self, answers):
        self.answers = answers

    def add_answer(self, answer):
        self.answers.append(answer)

    def get_answer(self, pos):
        return self.answers[pos]
