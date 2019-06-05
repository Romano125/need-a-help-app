# Generated by Django 2.1.5 on 2019-05-22 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20190522_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='currency',
            field=models.CharField(choices=[('EUR', '€'), ('GBP', '£'), ('AUD', '$ (Australian dollar)'), ('USD', '$ (United States dollar)'), ('CAD', '$ (Canadian dollar)'), ('HRK', 'kn'), ('CZK', 'Kč'), ('HUF', 'Ft'), ('CHF', 'Fr'), ('RON', 'lei'), ('RSD', 'din'), ('SEK', 'kr')], default='EUR', max_length=10),
        ),
        migrations.AlterField(
            model_name='requests',
            name='currency',
            field=models.CharField(choices=[('EUR', '€'), ('GBP', '£'), ('AUD', '$ (Australian dollar)'), ('USD', '$ (United States dollar)'), ('CAD', '$ (Canadian dollar)'), ('HRK', 'kn'), ('CZK', 'Kč'), ('HUF', 'Ft'), ('CHF', 'Fr'), ('RON', 'lei'), ('RSD', 'din'), ('SEK', 'kr')], default='EUR', max_length=10),
        ),
    ]