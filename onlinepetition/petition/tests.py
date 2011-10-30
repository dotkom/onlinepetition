from django.test import TestCase

from petition.models import Signature, Campaign


class SignatureTest(TestCase):
    def setUp(self):
        self.sign1 = Signature(name="Dag Olav", email="dagolav@prestegarden.com")
        self.sign2 = Signature(name="Ol Dagav", email="dagolap@stud.ntnu.no")

    def test_returns_correct_domain(self):
        self.assertEqual("prestegarden.com", self.sign1.domain)


class CampaignTest(TestCase):
    def setUp(self):
        self.camp1 = Campaign(title="TestCampaign", description="This is a test campaign")
        self.sign1 = Signature(name="Dag Olav", email="dagolav@prestegarden.com", campaign=self.camp1)
        self.sign2 = Signature(name="Ol Dagav", email="dagolap@stud.ntnu.no", campaign=self.camp1)
        self.sign1.save()
        self.sign2.save()

    def test_campaign_returns_all_signatures(self):
        self.assertEqual(2, self.camp1.signature_set.count())
    
    def test_campaign_returns_all_signature_domain(self):
        self.assertEqual(2, len(self.camp1.signed_domains))
        self.assertEqual("prestegarden.com", self.camp1.signed_domains[0])
        self.assertEqual("stud.ntnu.no", self.camp1.signed_domains[1])


