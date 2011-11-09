# -*- coding: utf-8 -*-

import datetime
import hashlib
import operator

from base64 import urlsafe_b64encode, urlsafe_b64decode
from collections import defaultdict

from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.db import models

from settings import ONLINE_PETITION_FROM_ADDRESS, ONLINE_PETITION_SECRET, DEPLOYMENT_ROOT_URL

from django.utils.translation import ugettext_lazy as _


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
    
    def is_satisfied_by(self, domain):
        return domain.endswith(self.name)
    
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
        return map(lambda x: x.name + " - " + self.obscured_field(getattr(x, 'email')),
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

    @property
    def signed_domains(self):
        return [s.domain for s in self.signature_set.filter(is_verified=True)]

    @property
    def domain_stats(self):
        if self.valid_domains.count() == 0:
            return sorted([(domain, self.signed_domains.count(domain)) for domain in set(self.signed_domains)], key=operator.itemgetter(1), reverse=True)[:5]
        result_map = defaultdict(int)
        for d in self.signed_domains:
            for vd in sorted(self.valid_domains.all(), key=lambda d: d.name.count('.')) :
                if vd.is_satisfied_by(d):
                    result_map[vd.name] += 1
                    break
        return sorted(result_map.items(), key=operator.itemgetter(1), reverse=True)[:5]

    @property
    def is_active(self):
        return self.start_date <= datetime.datetime.now() and self.end_date >= datetime.datetime.now() 

    def obscured_field(self, field):
        alpha_index = field.rfind('@')
        dot_index = field.rfind('.')

        return field[:alpha_index] + '@xxxxxxxx' + field[dot_index:]

    def is_valid_domain(self, users_email):
        valid_domains = Domain.objects.filter(campaign__id=self.id)
        if len(valid_domains) == 0:
            return True
        else:
            user_domain = get_domain_from_email(users_email)
            for valid in valid_domains:
                if user_domain.endswith(valid.name):
                    return True
        return False

    class Meta:
        verbose_name = _("campaign")
        verbose_name_plural = _("campaigns")


class Signature(models.Model):
    name = models.CharField(_("name"), max_length=100)
    email = models.CharField(_("e-mail"),
                             max_length=255) # if their longer then this, their problem for having an idiotic email ..
    signed_date = models.DateTimeField(_("signed_date"), auto_now_add=True)
    campaign = models.ForeignKey(Campaign)
    is_verified = models.BooleanField(_("is_verified"), default=False)

    @property
    def domain(self):
        alpha_index = self.email.rfind('@')
        return self.email[alpha_index + 1:]

    def get_salt(self):
        return hashlib.sha256(
            ONLINE_PETITION_SECRET + unicode(self.campaign.start_date) + unicode(
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

        send_mail(_(u'OnlinePetition - Verify signature for campaign ') + self.campaign.title,
                  _(u"""
You (or someone else pretending to be you) have requested to sign
a petition for {0:>s}

You can view the petition request at
{1:>s}

If you still agree to sign this petition, please click the link below
{2:>s}

-- 
OnlinePetition
Automatic email generator
""").format(self.campaign.title,
                             DEPLOYMENT_ROOT_URL + reverse('campaign_details', args=[self.campaign.pk, ]),
                             DEPLOYMENT_ROOT_URL + reverse('campaign_activate',
                                                           args=[self.campaign.pk, uri_b64encode(self.email), activate, ])),
                  ONLINE_PETITION_FROM_ADDRESS, (self.email,), fail_silently=False)

    class Meta:
        ordering = ['-is_verified', 'signed_date']
        verbose_name = _("signature")
        verbose_name_plural = _("signatures")



