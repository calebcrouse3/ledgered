# Generated by Django 3.2.8 on 2021-11-16 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledgered_app', '0002_auto_20211112_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='date',
            field=models.DateField(),
        ),
    ]
