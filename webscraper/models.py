from django.db import models
from datetime import date


class Webscraper(models.Model):
    store = models.CharField(max_length=15)
    item_name = models.CharField(max_length=255)
    item_image = models.CharField(default="default.jpg", max_length=255)
    item_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    item_quantity = models.CharField(max_length=20,null=True)
    unit_price = models.CharField(max_length=20, null=True) 
    item_searched = models.CharField(max_length=50)
    date_searched = models.DateField(default=date.today)
    item_url = models.CharField(max_length=255)

    def __str__(self):
        return self.item_name