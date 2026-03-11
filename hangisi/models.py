import datetime
from django.contrib import admin
from django.db import models
from django.utils import timezone

class Soru(models.Model):
    soru_metni = models.CharField(max_length=200)
    yayinlanma_tarihi = models.DateTimeField("Yayımlanma Tarihi")

    def __str__(self):
        return self.soru_metni

    @admin.display(
        boolean=True,
        ordering="yayinlanma_tarihi",
        description="Yakın zamanda yayımlandı mı?",
    )
    def was_published_recently(self):
        simdi = timezone.now()
        return simdi - datetime.timedelta(days=1) <= self.yayinlanma_tarihi <= simdi


class Secenek(models.Model):
    soru = models.ForeignKey(Soru, on_delete=models.CASCADE)
    secenek_metni = models.CharField(max_length=200)
    oylar = models.IntegerField(default=0)

    def __str__(self):
        return self.secenek_metni
