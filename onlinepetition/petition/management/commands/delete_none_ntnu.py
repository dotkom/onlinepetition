#from django.core.management.base import NoArgsCommand
from django.core.management.base import BaseCommand, CommandError
from petition.models import Signature
from petition.models import Campaign

class Command(BaseCommand):
    help = "Deletes all petition entries that is not retistered with an"\
    " NTNU-email"
    
    def handle(self, *args, **kwargs):
        valid_domains = ['@stud.ntnu.no', '@ntnu.no']
        for campain_id in args:
            #error, if the campaign does not exist
            try:
                campain = Campaign.objects.filter(pk=int(campain_id))
            except Campaign.DoesNotExist:
                raise CommandError('Campaign ID %s does not exits' %campain_id)

            signatures_qs = Signature.objects.filter(
                    campaign__pk =  int(campain_id))
            for domain in valid_domains:
                signatures_qs = signatures_qs.exclude(email__endswith = domain)

            for signature in signatures_qs:
                signature.delete()
