# Generated by Django 2.1.5 on 2019-03-23 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requests',
            name='address',
        ),
    ]