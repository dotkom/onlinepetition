from django.contrib import admin
from onlinepetition.mysite import Kampanje

class KampanjeAdmin(admin.ModelAdmin):
    list_display = ('tittel', 'startdato', 'sluttdato',) 

admin.site.register(Kampanje, KampanjeAdmin)
