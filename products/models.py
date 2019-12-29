from django.db import models


class Manufacturer(models.Model):
    name = models.CharField(max_length=120)
    url = models.URLField()


class Product(models.Model):
    product_key = models.CharField(max_length=16)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    identical = models.ManyToManyField('self')
    similar = models.ManyToManyField('self')