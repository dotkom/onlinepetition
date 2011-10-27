from django import forms
from django.utils.translation import ugettext_lazy as _

class CampaignRegistrationForm(forms.Form):
    id = "campaign_registration_form"
    email = forms.EmailField("email", required=True, label=_("Email"))
    name = forms.CharField("name", required=True, label=_("Name"))

    def clean(self):
        if self._errors:
            return
        return self.cleaned_data


