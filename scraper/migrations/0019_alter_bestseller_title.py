# Generated by Django 5.1.5 on 2025-03-13 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0018_bestseller'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bestseller',
            name='title',
            field=models.CharField(max_length=500),
        ),
    ]
