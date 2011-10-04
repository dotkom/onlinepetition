from django import forms


class CampaignRegistrationForm(forms.Form):
    id = "campaign_registration_form"
    email = forms.EmailField("email")

    def clean(self):
        if self._errors:
            return
        return self.cleaned_data


