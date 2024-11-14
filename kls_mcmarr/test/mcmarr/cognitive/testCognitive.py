import unittest
import json
import os

from kls_mcmarr.mcmarr.cognitive.CognitiveMcmarr import CognitiveMcmarr


class TestSetOfQuestions(unittest.TestCase):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        os.chdir("../../")

    @classmethod
    def tearDownClass(cls):
        os.chdir("kls_mcmarr/test/")
        pass

    def setUp(self):
        self.cognitive = CognitiveMcmarr()
        print(os.getcwd())
        self.cognitive.load_questions("assets/questions/questions.xml")

    def test_from_dict(self):
        sample_data = self.cognitive.to_dict()
        from_dict = CognitiveMcmarr.from_dict(sample_data)

        self.assertEqual(from_dict.to_dict(), self.cognitive.to_dict())

    def test_from_json(self):
        json_str = '{"set_of_questions": \
                        {"questions": \
                             [ \
                                 {"question": "¿Cual es el primer movimiento del Set de Bloqueos I?", \
                                  "id": 1, \
                                  "correct_answer_pos": 0, \
                                  "answers": [ \
                                      "Bloqueo Hacia Arriba", \
                                      "Bloqueo Hacia Dentro", \
                                      "Bloqueo Hacia Afuera", \
                                      "Bloqueo Hacia Abajo"]}, \
                                 {"question":"¿Qué se enfatiza en la ejecución de todos los bloqueos en el set de bloqueos 1?", \
                                  "id": 2, \
                                  "correct_answer_pos": 1, \
                                  "answers": ["Fuerza", \
                                              "Tecnica", \
                                              "Velocidad", \
                                              "Agresividad"]} \
                             ] \
                        } \
                    }'

        set_of_questions = CognitiveMcmarr.from_json(json_str)

        questions = set_of_questions.get_set()

        question_0 = questions.questions[0]
        self.assertEqual(question_0.get_question(), "¿Cual es el primer movimiento del Set de Bloqueos I?")
        self.assertEqual(question_0.get_id(), 1)
        self.assertEqual(question_0.get_correct_answer_pos(), 0)
        self.assertEqual(question_0.get_answer(0), "Bloqueo Hacia Arriba")
        self.assertEqual(question_0.get_answer(1), "Bloqueo Hacia Dentro")
        self.assertEqual(question_0.get_answer(2), "Bloqueo Hacia Afuera")
        self.assertEqual(question_0.get_answer(3), "Bloqueo Hacia Abajo")
        self.assertEqual(question_0.get_correct_answer(), "Bloqueo Hacia Arriba")

        question_1 = questions.questions[1]
        self.assertEqual(question_1.get_question(), "¿Qué se enfatiza en la ejecución de todos los bloqueos en el set de bloqueos 1?")
        self.assertEqual(question_1.get_id(), 2)
        self.assertEqual(question_1.get_correct_answer_pos(), 1)
        self.assertEqual(question_1.get_answer(0), "Fuerza")
        self.assertEqual(question_1.get_answer(1), "Tecnica")
        self.assertEqual(question_1.get_answer(2), "Velocidad")
        self.assertEqual(question_1.get_answer(3), "Agresividad")
        self.assertEqual(question_1.get_correct_answer(), "Tecnica")

    def test_to_dict(self):
        json_str = '{"set_of_questions": \
                        {"questions": \
                             [ \
                                 {"question": "¿Cual es el primer movimiento del Set de Bloqueos I?", \
                                  "id": 1, \
                                  "correct_answer_pos": 0, \
                                  "answers": [ \
                                      "Bloqueo Hacia Arriba", \
                                      "Bloqueo Hacia Dentro", \
                                      "Bloqueo Hacia Afuera", \
                                      "Bloqueo Hacia Abajo"]}, \
                                 {"question":"¿Qué se enfatiza en la ejecución de todos los bloqueos en el set de bloqueos 1?", \
                                  "id": 2, \
                                  "correct_answer_pos": 1, \
                                  "answers": ["Fuerza", \
                                              "Tecnica", \
                                              "Velocidad", \
                                              "Agresividad"]} \
                             ] \
                        } \
                    }'

        set_of_questions = CognitiveMcmarr.from_json(json_str)
        dict = set_of_questions.to_dict()
        expected_dict = json.loads(json_str)

        self.assertEqual(dict, expected_dict)

    def test_to_json(self):
        json_str = '{"set_of_questions": \
                        {"questions": \
                             [ \
                                 {"question": "¿Cual es el primer movimiento del Set de Bloqueos I?", \
                                  "id": 1, \
                                  "correct_answer_pos": 0, \
                                  "answers": [ \
                                      "Bloqueo Hacia Arriba", \
                                      "Bloqueo Hacia Dentro", \
                                      "Bloqueo Hacia Afuera", \
                                      "Bloqueo Hacia Abajo"]}, \
                                 {"question":"¿Qué se enfatiza en la ejecución de todos los bloqueos en el set de bloqueos 1?", \
                                  "id": 2, \
                                  "correct_answer_pos": 1, \
                                  "answers": ["Fuerza", \
                                              "Tecnica", \
                                              "Velocidad", \
                                              "Agresividad"]} \
                             ] \
                        } \
                    }'

        set_of_movements = CognitiveMcmarr.from_json(json_str)
        to_json = set_of_movements.to_json()
        json_orig = json.loads(json_str)
        self.assertEqual(CognitiveMcmarr.from_json(to_json).to_dict(), json_orig)

    def test_save_answer(self):
        self.cognitive.save_answer(True, answer="Answer 1", question="Question 1", question_id=1, output_path="assets/output/capture/cognitive/")
        self.cognitive.save_answer(True, answer="Answer 2", question="Question 1", question_id=1, output_path="assets/output/capture/cognitive/")
        self.cognitive.save_answer(False, answer="Answer 1", question="Question 2", question_id=2, output_path="assets/output/capture/cognitive/")
        self.cognitive.save_answer(False, answer="Answer 2", question="Question 2", question_id=2, output_path="assets/output/capture/cognitive/")

if __name__ == '__main__':
    unittest.main()
