# Generated by Django 2.1.5 on 2019-04-18 18:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appliccation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repairman', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ClientNotifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification', models.CharField(max_length=1000)),
                ('url_to_go', models.CharField(default='-', max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('seen', models.BooleanField(default=False)),
                ('remove', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Hire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repairman', models.IntegerField()),
                ('status', models.CharField(default='pending', max_length=100)),
                ('accepted', models.BooleanField(default=False)),
                ('done', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='JobHire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='pending', max_length=100)),
                ('done', models.BooleanField(default=False)),
                ('date_hired', models.DateTimeField(auto_now_add=True)),
                ('repairman', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('male', 'MALE'), ('female', 'FEMALE')], max_length=10)),
                ('address', models.CharField(max_length=50)),
                ('birth_date', models.DateField(null=True)),
                ('phone_number', models.CharField(max_length=100)),
                ('costs', models.IntegerField(default=100)),
                ('role', models.CharField(choices=[('client', 'CLIENT'), ('repairman', 'REPAIRMAN')], max_length=15)),
                ('profession', models.CharField(choices=[('bricklayer', 'bricklayer'), ('builder', 'builder'), ('carpenter', 'carpenter'), ('chimney sweep', 'chimney sweep'), ('cleaner', 'cleaner'), ('decorator', 'decorator'), ('electrician', 'electrician'), ('gardener', 'gardener'), ('glazier', 'glazier'), ('groundsman', 'groundsman'), ('pest controller', 'pest controller'), ('mechanic', 'mechanic'), ('plasterer', 'plasterer'), ('plumber', 'plumber'), ('roofer', 'roofer'), ('stonemason', 'stonemason'), ('tiler', 'tiler'), ('welder', 'welder'), ('window cleaner', 'window cleaner'), ('Other', 'Other')], default='Other', max_length=250)),
                ('knowledges', models.TextField(max_length=1000)),
                ('rating', models.FloatField(default=0.0)),
                ('rated', models.IntegerField(default=0)),
                ('hired', models.IntegerField(default=0)),
                ('num_hires', models.IntegerField(default=0)),
                ('photo', models.ImageField(default='default_user.jpg', upload_to='profile_user')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.IntegerField()),
                ('feedback', models.CharField(max_length=1000)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('repairman', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repairman', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RepairmanNotifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification', models.CharField(max_length=1000)),
                ('url_to_go', models.CharField(default='-', max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('seen', models.BooleanField(default=False)),
                ('remove', models.BooleanField(default=False)),
                ('repairman', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RepairmanRequests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.IntegerField()),
                ('request_message', models.CharField(default='No request', max_length=1000)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('seen', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=False)),
                ('done', models.BooleanField(default=False)),
                ('repairman', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RequestImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(default='default_request.jpg', upload_to='requests_user')),
            ],
        ),
        migrations.CreateModel(
            name='Requests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(max_length=30)),
                ('required_knowledges', models.TextField(max_length=1000)),
                ('price', models.IntegerField()),
                ('address', models.CharField(max_length=30)),
                ('job_description', models.TextField(max_length=1000)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ImageField(default='default_request.jpg', upload_to='requests_user')),
                ('visible', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SeenRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seen', models.BooleanField(default=False)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Requests')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserFavourite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.IntegerField()),
                ('repairman', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='requestimages',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Requests'),
        ),
        migrations.AddField(
            model_name='jobhire',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Requests'),
        ),
        migrations.AddField(
            model_name='appliccation',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Requests'),
        ),
    ]
