import datetime
import hashlib

from base64 import urlsafe_b64encode, urlsafe_b64decode

from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.db import models

from settings import ONLINE_PETITION_FROM_ADDRESS, ONLINE_PETITION_SECRET, DEPLOYMENT_ROOT_URL

from django.utils.translation import gettext_lazy as _


def get_domain_from_email(email):
    alpha_index = email.rfind('@')
    return email[alpha_index + 1:]

def uri_b64encode(s):
     return urlsafe_b64encode(s).strip('=')

def uri_b64decode(s):
     return urlsafe_b64decode(s + '=' * (4 - len(s) % 4))

class Domain(models.Model):
    name = models.CharField(_("domain"), max_length=255, unique=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _("domain")
        verbose_name_plural = _("domains")


class Campaign(models.Model):
    title = models.CharField(_("title"), max_length=50)
    description = models.TextField(_("description"))
    start_date = models.DateTimeField(_("start_date"), default=datetime.datetime.now)
    end_date = models.DateTimeField(_("end_date"), default=datetime.datetime.now)
    valid_domains = models.ManyToManyField(Domain, verbose_name=_('valid domains'),
                                           help_text=_('If no domains are chosen, every signature request is accepted.'),
                                           blank=True)

    def __unicode__(self):
        return self.title

    @property
    def signatures(self):
        return map(lambda x: self.obscured_field(getattr(x, 'email')),
                   Signature.objects.filter(campaign=self, is_verified=True))

    def is_registered(self, email_to_check_for):
        return Signature.objects.filter(campaign=self, email=email_to_check_for)

    @property
    def active_campaigns_count(self):
        return Campaign.objects.filter(start_date__lte=datetime.datetime.now(), 
                                       end_date__gte=datetime.datetime.now()).count()

    @property
    def active_signatures_count(self):
        return self.signature_set.filter(is_verified=True).count()

    @property
    def not_verified_signatures_count(self):
        return self.signature_set.filter(is_verified=False).count()

    def obscured_field(self, field):
        alpha_index = field.rfind('@')
        dot_index = field.rfind('.')

        return field[:alpha_index] + '@xxxxxxxxxxxxxxxxxxxx' + field[dot_index:]

    def is_valid_domain(self, users_email):
        valid_domains = Domain.objects.filter(campaign__id=self.id)
        if len(valid_domains) == 0:
            return True
        else:
            return get_domain_from_email(users_email) in map(lambda x: getattr(x, 'name'), valid_domains)

    class Meta:
        verbose_name = _("campaign")
        verbose_name_plural = _("campaigns")


class Signature(models.Model):
    email = models.CharField(_("email"),
                             max_length=255) # if their longer then this, their problem for having an idiotic email ..
    signed_date = models.DateTimeField(_("signed_date"), auto_now_add=True)
    campaign = models.ForeignKey(Campaign)
    is_verified = models.BooleanField(_("is_verified"), default=False)

    def get_salt(self):
        return hashlib.sha256(
            ONLINE_PETITION_SECRET + self.campaign.title + unicode(self.campaign.start_date) + unicode(
                self.campaign.end_date)).hexdigest()


    def verify_hash(self, hash):
        salt = self.get_salt()

        correct_hash = hashlib.sha256(salt + self.email + unicode(self.signed_date)).hexdigest()
        if hash == correct_hash:
            self.is_verified = True
            self.save()
            return True
        return False

    def send_verify_email(self):
        salt = self.get_salt()
        activate = hashlib.sha256(salt + self.email + unicode(self.signed_date)).hexdigest()

        send_mail('OnlinePetition - Verify signature for campaign ' + self.campaign.title,
                  u"""
                  You (or someone else pretending to be you) have requested to sign
                  a petition for "{0:>s}".

                  You can view the petition request at
                  {1:>s}

                  If you still agree to sign this petition, please click the link below
                  {2:>s}

                  --
                  OnlinePetition
                  Automatic email generator
                  """.format(self.campaign.title,
                             DEPLOYMENT_ROOT_URL + reverse('campaign_details', args=[self.campaign.pk, ]),
                             DEPLOYMENT_ROOT_URL + reverse('campaign_activate',
                                                           args=[self.campaign.pk, uri_b64encode(self.email), activate, ])),
                  ONLINE_PETITION_FROM_ADDRESS, (self.email,), fail_silently=False)

    class Meta:
        ordering = ['-is_verified', 'signed_date']
        verbose_name = _("signature")
        verbose_name_plural = _("signatures")



