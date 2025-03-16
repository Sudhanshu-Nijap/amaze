# Generated by Django 5.1.5 on 2025-03-05 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0003_alter_pricehistory_user_alter_trackedproduct_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackedproduct',
            name='target_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
