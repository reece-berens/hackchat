# Generated by Django 3.0.3 on 2020-04-26 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_channelpermissions_lastreadmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='containsBannedPhrase',
            field=models.BooleanField(default=False),
        ),
    ]
