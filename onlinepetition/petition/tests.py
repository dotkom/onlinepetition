"""
OnlinePetition tests.

Run with  manage.py test petition
"""
from datetime import datetime, timedelta

from django.test import TestCase

from petition.models import Signature, Campaign, Domain

class SignatureTest(TestCase):
    def setUp(self):
        self.sign1 = Signature.objects.create(name="Dag Olav", email="dagolav@prestegarden.com")
        self.sign2 = Signature.objects.create(name="Ol Dagav", email="dagolap@stud.ntnu.no")

    def test_returns_correct_domain(self):
        self.assertEqual("prestegarden.com", self.sign1.domain)
        

class CampaignTest(TestCase):
    def setUp(self):
        self.camp1 = Campaign.objects.create(title="TestCampaign", description="This is a test campaign")
        self.sign1 = Signature.objects.create(name="Dag Olav", email="dagolav@prestegarden.com", campaign=self.camp1, is_verified=True)
        self.sign2 = Signature.objects.create(name="Ol Dagav", email="dagolap@stud.ntnu.no", campaign=self.camp1, is_verified=True)
        self.sign3 = Signature.objects.create(name="Test Olav", email="dag.olav@prestegarden.com", campaign=self.camp1, is_verified=True)
        
        self.lots_of_signatures = []
        for i in xrange(10):
            sign = Signature.objects.create(name="Name "+str(i), email="email@"+str(i)+".com", campaign=self.camp1, is_verified=True)
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


class DomainTest(TestCase):
    def setUp(self):
        self.valid_domain = Domain.objects.create(name="uib.no")

        self.campaign = Campaign.objects.create(
            title="Test",
            description="descriptionfoo",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(hours=1),
            )
        
    def test_valid_domains_ends_with(self):
        self.assertTrue(self.campaign.is_valid_domain('foobar@troll.no'))
        self.campaign.valid_domains.add(self.valid_domain)
        self.assertFalse(self.campaign.is_valid_domain('foobar@troll.no'))
        self.assertTrue(self.campaign.is_valid_domain('student@stud.uib.no'))
        self.assertTrue(self.campaign.is_valid_domain('admin@uib.no'))


class CampaignSpecialCasesTests(TestCase):
    def setUp(self):
        self.camp2 = Campaign.objects.create(title="Test", description="Test")
        self.signsingle = Signature.objects.create(name="TestName", email="test@test.com", campaign=self.camp2, is_verified=True)
        self.signsecond = Signature.objects.create(name="NonVerified", email="test2@test2.com", campaign=self.camp2, is_verified=False)

    def test_only_verified_signatures_should_count_towards_domain_stats(self):
        self.assertEqual(1, len(self.camp2.domain_stats))


class CampaignWithValidDomainsTests(TestCase):
    def setUp(self):
        self.camp = Campaign.objects.create(title="Test", description="Test")
        self.valid_domain = Domain.objects.create(name="ntnu.no")
        self.valid_subdomain = Domain.objects.create(name="stud.ntnu.no")

    def test_all_domains_should_be_counted_if_no_list_of_valid_is_set(self):
        sign1 = Signature.objects.create(name="From stud ntnu", email="dagolap@stud.ntnu.no", campaign=self.camp, is_verified=True)
        sign2 = Signature.objects.create(name="From idi ntnu", email="dagolap@idi.ntnu.no", campaign=self.camp, is_verified=True)
        self.assertEqual(2, len(self.camp.domain_stats))

    def test_only_domains_from_valid_domain_list_is_contained_in_stats(self):
        self.camp.valid_domains.add(self.valid_domain)
        sign1 = Signature.objects.create(name="From stud ntnu", email="dagolap@stud.ntnu.no", campaign=self.camp, is_verified=True)
        sign2 = Signature.objects.create(name="From idi ntnu", email="dagolap@idi.ntnu.no", campaign=self.camp, is_verified=True)
        domain_in_stats = self.camp.domain_stats[0][0]
        self.assertEqual(1, len(self.camp.domain_stats))
        self.assertEqual("ntnu.no", domain_in_stats)

    def test_statistics_should_count_towards_the_topmost_domain_allowed(self):
        self.camp.valid_domains.add(self.valid_subdomain)
        self.camp.valid_domains.add(self.valid_domain)
        Signature.objects.create(name="Dag Olav", email="dagolap@stud.ntnu.no", campaign=self.camp, is_verified=True)
        self.assertEqual("ntnu.no", self.camp.domain_stats[0][0])
