from django import forms
#from django.utils.translation import gettext_lazy as _

class CampaignRegistrationForm(forms.Form):
    id = "campaign_registration_form"
    email = forms.EmailField("email")

    def clean(self):
        if self._errors:
            return
        return self.cleaned_data


