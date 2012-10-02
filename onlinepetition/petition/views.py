# -*- coding: utf-8 -*-

import datetime
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from petition.forms import CampaignRegistrationForm
from petition.models import Campaign, Signature, uri_b64decode

def list(request):
    running_campaigns = Campaign.objects.filter(start_date__lte=datetime.datetime.now(), end_date__gte=datetime.datetime.now())
    return render_to_response('petition/index.html',
            {'campaigns': running_campaigns,
             'campaign_count': len(running_campaigns), # hmf, need to make it use model  maybe? yawn
        },
                              context_instance=RequestContext(request))

def latest(request):
    campaigns = Campaign.objects.filter(start_date__lte=datetime.datetime.now(),
                                       end_date__gte=datetime.datetime.now()).reverse()
    if not campaigns:
        return list(request)
        
    return details(request, campaigns[0].id)

def details(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)

    form = CampaignRegistrationForm() # legge til email?

    return render_to_response('petition/details.html', { 'form': form,
        'campaign': campaign,
        'campaign_count': campaign.active_campaigns_count,
        'campaign_signatures_count': campaign.active_signatures_count,
        'campaign_signatures_notverified_count': campaign.not_verified_signatures_count,
        },
                              context_instance=RequestContext(request))


def register(request, campaign_id):
    try:
        should_redirect = False
        campaign = None
        template = 'petition/register_form.html'

        try:
            campaign = Campaign.objects.get(pk=campaign_id)
        except Campaign.DoesNotExist:
            messages.error(request, _('Campaign you tried to register for, doesn\'t exist.'))

        if campaign and request.method == 'POST':
            form = CampaignRegistrationForm(request.POST)

            if not campaign.is_active:
                messages.warning(request, _('The chosen campaign is not currently open for new signatures'))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('campaign_list')))

            if form.is_valid():
                users_email = form.cleaned_data['email']
                users_name = form.cleaned_data['name']

                if not users_email:
                    messages.error(request, _('Empty email address submited, please submit a valid one'))
                else:
                    if not campaign.is_valid_domain(users_email):
                        messages.error(request, _('Your email is not listed amongst the domains that are allowed to participate in this campaign!'))
                    elif not campaign.is_registered(users_email):
                        try:
                            signature_request = Signature()
                            signature_request.email = users_email
                            signature_request.name = users_name
                            signature_request.campaign = campaign
                            signature_request.save()

                            # some kind of try / catch around this one?
                            # transaction? yawn.
                            signature_request.send_verify_email()
                            messages.warning(request,
                                             _('Your signature is receieved. You MUST click on the link sent to you by email in order for your signature to be approved.'))
                            #template = 'petition/details.html'
                        except Exception, e:
                            messages.error(request, _('Ooops, something went wrong ..'))
                            messages.error(request, e)
                            signature_request.delete()
                            print(str(e))
                    else:
                        messages.error(request, _('You are already registered to this campaign!'))

                    should_redirect = True
            else:
                messages.error(request, _('Blubb blubb, we do require a valid email address for registration'))
        else:
            form = CampaignRegistrationForm()

        response_dict = {
            'form': form,
            'campaign': campaign,
            'campaign_signatures_count': campaign.active_signatures_count,
            'campaign_signatures_notverified_count': campaign.not_verified_signatures_count,
            }

        if should_redirect:
            return HttpResponseRedirect(reverse(details, args=[campaign.pk]))
        else:
            return render_to_response(template, response_dict, context_instance=RequestContext(request))

    except Exception, e:
        print(str(e))


def activate(request, campaign_id, email, hash):
    signature = None

    campaign = get_object_or_404(Campaign, pk=campaign_id)

    try:
        # required to cast email to str from unicode due to uri_b64decode doesn't like unicode strings.
        signature = Signature.objects.get(email=uri_b64decode(str(email)), campaign=campaign)
        if signature and not signature.is_verified:
            if not signature.verify_hash(hash):
                messages.error(request,
                               _('Failed to activate signature, make sure you enter the activation code exactly as in the email!'))
            else:
                messages.success(request, _('Your signature is now verified and added to the campaign!'))
        elif signature.is_verified:
            messages.warning(request, _('Signature already verified!'))
        else:
            messages.error(request, _('Failed to find signature to activate!'))

    except Signature.DoesNotExist:
        messages.error(request, _('Failed to find signature to activate!'))

    return HttpResponseRedirect(reverse(details, args=[campaign_id]))


def about(request):
    running_campaigns = Campaign.objects.filter(start_date__gte=datetime.date.today())
    return render_to_response('petition/about.html', {},
                              context_instance=RequestContext(request))


def faq(request):
    running_campaigns = Campaign.objects.filter(start_date__gte=datetime.date.today())
    return render_to_response('petition/faq.html', {},
                              context_instance=RequestContext(request))

def mylogin(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                # success
                messages.success(request, _("You are now logged in!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('campaign_list')))

    messages.error(request, _("Login failed")) #TODO: Handle reasons for failed login :)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('campaign_list')))

def mylogout(request):
    logout(request)
    messages.success(request, _("You are now logged out!"))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('campaign_list')))
