import unittest
import os

from kls_mcmarr.kls.affective.Affective import Affective


class TestSetOfQuestions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.chdir("../../")

    @classmethod
    def tearDownClass(cls):
        os.chdir("kls_mcmarr/test/")
        pass

    def setUp(self):
        self.affective = Affective()
        print(os.getcwd())

    def test_affective(self):
        inferred_status = self.affective.get_affective_status("assets/example/image_test_affective_surprise.png")

        self.assertEqual(inferred_status, "Positivo")

        inferred_status = self.affective.get_affective_status("assets/example/image_test_affective_disgust.png")

        self.assertEqual(inferred_status, "Negativo")
