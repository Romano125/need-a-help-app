# Generated by Django 2.1.5 on 2019-05-17 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20190517_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='address',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='requests',
            name='address',
            field=models.CharField(max_length=30),
        ),
    ]
