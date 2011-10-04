from django.contrib import admin
from petition.models import Campaign, Signature

class SignatureInline(admin.TabularInline):
    model = Signature
    extra = 3

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date',)

    inlines = [SignatureInline]

admin.site.register(Campaign, CampaignAdmin)
