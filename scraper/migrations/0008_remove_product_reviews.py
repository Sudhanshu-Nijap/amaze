# Generated by Django 5.1.5 on 2025-03-08 05:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0007_alter_customuser_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='reviews',
        ),
    ]
