# Generated by Django 2.1.3 on 2019-03-10 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientnotifications',
            name='remove',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='repairmannotifications',
            name='remove',
            field=models.BooleanField(default=False),
        ),
    ]
