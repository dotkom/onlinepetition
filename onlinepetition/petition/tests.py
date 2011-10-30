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
        self.sign1 = Signature(name="Dag Olav", email="dagolav@prestegarden.com", campaign=self.camp1, is_verified=True)
        self.sign2 = Signature(name="Ol Dagav", email="dagolap@stud.ntnu.no", campaign=self.camp1, is_verified=True)
        self.sign3 = Signature(name="Test Olav", email="dag.olav@prestegarden.com", campaign=self.camp1, is_verified=True)
        self.sign1.save()
        self.sign2.save()
        self.sign3.save()
        
        self.lots_of_signatures = []
        for i in xrange(10):
            sign = Signature(name="Name "+str(i), email="email@"+str(i)+".com", campaign=self.camp1, is_verified=True)
            sign.save()
            self.lots_of_signatures.append(sign)


    def test_campaign_returns_all_signatures(self):
        self.assertEqual(13, self.camp1.signature_set.count())
    
    def test_campaign_returns_all_signature_domain(self):
        self.assertEqual(13, len(self.camp1.signed_domains))
        self.assertEqual("prestegarden.com", self.camp1.signed_domains[0])
        self.assertEqual("stud.ntnu.no", self.camp1.signed_domains[1])

    def test_campaign_return_correct_domain_stats_sorted_correctly(self):
        self.assertEqual(2, self.camp1.domain_stats[0][1])

    def test_campaign_domain_stats_only_return_top_5_domains(self):
        self.assertEqual(5, len(self.camp1.domain_stats))


class CampaignSpecialCasesTests(TestCase):
    def setUp(self):
        self.camp2 = Campaign(title="Test", description="Test")
        self.signsingle = Signature(name="TestName", email="test@test.com", campaign=self.camp2, is_verified=True)
        self.signsingle.save()
        self.signsecond = Signature(name="NonVerified", email="test2@test2.com", campaign=self.camp2, is_verified=False)
        self.signsecond.save()

    def test_only_verified_signatures_should_count_towards_domain_stats(self):
        self.assertEqual(1, len(self.camp2.domain_stats))
