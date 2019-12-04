from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField

# --- Logo Model --- Author: JCVBS

def custom_upload_to(instance, filename):
    old_instance = Logo.objects.get(pk = instance.pk)
    old_instance.avatar.delete()

    return 'logo/' + filename

class Logo(models.Model):
    image = models.ImageField(upload_to = custom_upload_to)

