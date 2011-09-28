from django.db import models

# Create your models here.
class Kampanje(models.Model):
    tittel = models.CharField("tittel", max_length=50)
    beskrivelse = models.TextField("beskrivelse")
    start_dato = models.DateTimeField("startdato", auto_now_add=True)
    slutt_dato = models.DateTimeField("sluttdato", auto_now_add=True)

class Underskrift(models.Model):
    bruker_navn = models.CharField("navn", max_length=12)
    kampanje = models.ForeignKey(Kampanje)

