# Generated by Django 2.1.3 on 2019-06-05 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20190522_1722'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clientmessage',
            old_name='url_to_go',
            new_name='url_to_go_client',
        ),
        migrations.AddField(
            model_name='clientmessage',
            name='url_to_go_sender',
            field=models.CharField(default='-', max_length=200),
        ),
    ]