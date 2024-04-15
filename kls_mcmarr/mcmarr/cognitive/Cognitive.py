from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
from kls_mcmarr.mcmarr.cognitive.Question import Question
from kls_mcmarr.mcmarr.cognitive.SetOfQuestions import SetOfQuestions
import json


class Cognitive(ABC):

    def __init__(self):
        self.set_of_questions = SetOfQuestions()

    @classmethod
    def from_dict(cls, data):
        cognitive = cls()
        if 'set_of_questions' in data:
            cognitive.set_of_questions = SetOfQuestions.from_dict(data['set_of_questions'])
        return cognitive

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self):
        dict_set = {'set_of_questions': self.set_of_questions.to_dict()}
        return dict_set

    def to_json(self):
        return json.dumps(self.to_dict())

    def load_questions(self, template_path):
        self.set_of_questions = self.xmlCognitiveTemplateLoader(template_path)

    def get_set(self):
        return self.set_of_questions

    def xmlCognitiveTemplateLoader(self, template_path):
        set_of_questions = SetOfQuestions()

        # Get root of xml file.
        if template_path is not None:
            root_xml = ET.parse(template_path).getroot()

            question_root_xml = root_xml.findall('question')
            for question_xml in question_root_xml:
                # Create object that encapsulates the movement.
                question = Question()

                # Get information about the question.
                question.question = question_xml.find('question').text
                question.correct_answer_pos = question_xml.find('correct-answer-pos').text

                # Get root of errors for this movement.
                if question_xml.findall('answers'):
                    answers_xml = question_xml.findall('answers')[0]
                    # Get each answer for this question.
                    for answer_xml in answers_xml.findall('answer'):
                        question.answers.append(answer_xml.text)

                # Append questions to the set.
                set_of_questions.add_question(question)

        # Return loaded set.
        return set_of_questions
