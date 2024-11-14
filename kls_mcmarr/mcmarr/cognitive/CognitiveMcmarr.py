import os
import json
import xml.etree.ElementTree as ET
from abc import ABC

from kls_mcmarr.mcmarr.cognitive.Question import Question
from kls_mcmarr.mcmarr.cognitive.SetOfQuestions import SetOfQuestions


class CognitiveMcmarr(ABC):

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
        self.set_of_questions = self.xml_cognitive_template_loader(template_path)

    def get_set(self):
        return self.set_of_questions

    def save_answer(self, correct, question, answer, question_id, output_path):
        if correct:
            answer_list = [True, question, answer, question_id]
        else:
            answer_list = [False, question, answer, question_id]

        # Construct the full file path
        file_path = os.path.join(output_path, str(question_id) + "-cognitive.txt")

        # Check if the path exists, if not, create.
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Check if the file exists and set the mode to append ('a') or create ('w')
        mode = 'a' if os.path.exists(file_path) else 'w'

        # Open the file in the determined mode and add the answer list
        with open(file_path, mode) as file:
            file.write(str(answer_list) + "\n")
            file.close()

    def xml_cognitive_template_loader(self, template_path):
        set_of_questions = SetOfQuestions()

        # Get root of xml file.
        if template_path is not None:
            root_xml = ET.parse(template_path).getroot()

            question_root_xml = root_xml.findall('question')
            for question_xml in question_root_xml:
                # Create object that encapsulates the movement.
                question = Question()

                # Get information about the question.
                question.id = question_xml.find('id').text
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
