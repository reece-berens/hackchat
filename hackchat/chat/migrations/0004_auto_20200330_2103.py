# Generated by Django 3.0.3 on 2020-03-31 02:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_auto_20200328_2110'),
    ]

    operations = [
        migrations.RenameField(
            model_name='channel',
            old_name='newUserPermissionStatus',
            new_name='defaultPermissionStatus',
        ),
    ]
