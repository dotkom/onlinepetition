from django.contrib import admin
from petition.models import Campaign, Signature, Domain

from django.utils.translation import gettext_lazy as _

class SignatureInline(admin.TabularInline):
    model = Signature
    extra = 3

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date',)
    fieldsets = (
        (None, {'fields': ('title', 'description',)}),
        (_('Registration period'), {'fields': ('start_date', 'end_date')}),
        (_('Requirements'), {'fields': ('valid_domains',)}),
    )

    filter_horizontal = 'valid_domains',
    inlines = [SignatureInline]


class DomainAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Domain, DomainAdmin)
