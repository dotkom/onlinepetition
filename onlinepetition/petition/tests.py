from django.test import TestCase

from petition.models import Signature


class SignatureTest(TestCase):
    def setUp(self):
        self.sign1 = Signature(name="Dag Olav", email="dagolav@prestegarden.com")
        self.sign2 = Signature(name="Ol Dagav", email="dagolap@stud.ntnu.no")

    def test_returns_correct_domain(self):
        self.assertEqual("prestegarden.com", self.sign1.domain)



class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
