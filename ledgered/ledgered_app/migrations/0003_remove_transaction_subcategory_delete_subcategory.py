# Generated by Django 4.1.4 on 2023-03-29 21:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ledgered_app', '0002_rename_ignored_uploadsummary_duplicate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='subcategory',
        ),
        migrations.DeleteModel(
            name='Subcategory',
        ),
    ]
