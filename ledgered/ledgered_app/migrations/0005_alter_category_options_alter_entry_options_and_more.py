# Generated by Django 4.1.4 on 2022-12-06 22:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ledgered_app', '0004_auto_20211116_2156'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'categories'},
        ),
        migrations.AlterModelOptions(
            name='entry',
            options={'verbose_name_plural': 'entries'},
        ),
        migrations.AlterModelOptions(
            name='subcategory',
            options={'verbose_name_plural': 'subcategories'},
        ),
    ]
