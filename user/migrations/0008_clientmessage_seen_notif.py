# Generated by Django 2.1.3 on 2019-06-05 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_auto_20190605_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientmessage',
            name='seen_notif',
            field=models.BooleanField(default=False),
        ),
    ]
