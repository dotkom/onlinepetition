from django import forms
from django.utils.translation import ugettext_lazy as _

class CampaignRegistrationForm(forms.Form):
    id = "campaign_registration_form"
    name = forms.CharField("name", required=True, label=_("Name"))
    email = forms.EmailField("email", required=True, label=_("Email"))

    def clean(self):
        if self._errors:
            return
        return self.cleaned_data


