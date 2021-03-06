# Generated by Django 4.0.1 on 2022-01-21 17:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Webscraper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store', models.CharField(max_length=15)),
                ('item_name', models.CharField(max_length=50)),
                ('item_image', models.ImageField(default='default.jpg', upload_to='scrapedimages')),
                ('item_price', models.DecimalField(decimal_places=2, max_digits=8, null=True)),
                ('unit_price', models.CharField(max_length=20, null=True)),
                ('item_searched', models.CharField(max_length=50)),
                ('date_searched', models.DateField(default=datetime.date.today)),
                ('item_url', models.CharField(max_length=255)),
            ],
        ),
    ]
