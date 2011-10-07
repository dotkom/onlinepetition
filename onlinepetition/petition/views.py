import datetime
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404

from django.contrib import messages
from petition.forms import CampaignRegistrationForm

from petition.models import Campaign, Signature, uri_b64decode

def list(request):
    running_campaigns = Campaign.objects.filter(start_date__lte=datetime.date.today(), end_date__gte=datetime.date.today())
    return render_to_response('petition/index.html',
            {'campaigns': running_campaigns,
             'campaign_count': Campaign.objects.count(), # hmf, need to make it use model  maybe? yawn
        },
                              context_instance=RequestContext(request))


def details(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)

    form = CampaignRegistrationForm() # legge til email?

    return render_to_response('petition/details.html', {
        'form': form,
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
            messages.error(request, 'Campaign you tried to register for, doesn\'t exist.')

        if campaign and request.method == 'POST':
            form = CampaignRegistrationForm(request.POST)

            if form.is_valid():
                users_email = form.cleaned_data['email']

                if not users_email:
                    messages.error(request, 'Empty email address submited, please submit a valid one')
                else:
                    if not campaign.is_valid_domain(users_email):
                        messages.error(request, 'Your email is not listed in the alloweded domains that are allowed to participate in this campaign!')
                    elif not campaign.is_registered(users_email):
                        try:
                            signature_request = Signature()
                            signature_request.email = users_email
                            signature_request.campaign = campaign
                            signature_request.save()

                            # some kind of try / catch around this one?
                            # transaction? yawn.
                            signature_request.send_verify_email()
                            messages.success(request,
                                             'Registrering mottatt, vennligst bekreft registrering via lenken som kommer pr. epost!')
                            #template = 'petition/details.html'
                        except Exception, e:
                            messages.error(request, 'Ooops, something went wrong ..')
                            signature_request.delete()
                            print(str(e))
                    else:
                        messages.error(request, 'You are already registered to this campaign!')

                    should_redirect = True
            else:
                messages.error(request, 'Blubb blubb, we do require a valid email address for registration')
        else:
            form = CampaignRegistrationForm()

        response_dict = {
            'form': form,
            'campaign': campaign,
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
                               'Failed to activate signature, make sure you enter the activation code exactly as in the email!')
            else:
                messages.success(request, 'Your signature is now verified and added to the campaign!')
        elif signature.is_verified:
            messages.warning(request, 'Signature already verified!')
        else:
            messages.error(request, 'Failed to find signature to activate!')

    except Signature.DoesNotExist:
        messages.error(request, 'Failed to find signature to activate!')

    return HttpResponseRedirect(reverse(details, args=[campaign_id]))


def about(request):
    running_campaigns = Campaign.objects.filter(start_date__gte=datetime.date.today())
    return render_to_response('petition/about.html', {},
                              context_instance=RequestContext(request))


def faq(request):
    running_campaigns = Campaign.objects.filter(start_date__gte=datetime.date.today())
    return render_to_response('petition/faq.html', {},
                              context_instance=RequestContext(request))

