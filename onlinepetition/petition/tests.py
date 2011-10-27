"""
OnlinePetition tests.

Run with  manage.py test petition
"""
from datetime import timedelta, datetime

from django.test import TestCase
from petition.models import Campaign, Signature, Domain


class PetitionTests(TestCase):

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

    