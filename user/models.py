from django.db import models
from django.urls import reverse
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from PIL import Image

ROLES = (
    ('client', 'CLIENT'),
    ('repairman', 'REPAIRMAN')
)

GENDER = (
    ('male', 'MALE'),
    ('female', 'FEMALE')
)

PROFESSION = (
    ('bricklayer', 'bricklayer'),
    ('builder', 'builder'),
    ('carpenter', 'carpenter'),
    ('chimney sweep', 'chimney sweep'),
    ('cleaner', 'cleaner'),
    ('decorator', 'decorator'),
    ('electrician', 'electrician'),
    ('gardener', 'gardener'),
    ('glazier', 'glazier'),
    ('groundsman', 'groundsman'),
    ('pest controller', 'pest controller'),
    ('mechanic', 'mechanic'),
    ('plasterer', 'plasterer'),
    ('plumber', 'plumber'),
    ('roofer', 'roofer'),
    ('stonemason', 'stonemason'),
    ('tiler', 'tiler'),
    ('welder', 'welder'),
    ('window cleaner', 'window cleaner'),
    ('Other', 'Other')
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=GENDER)
    address = models.CharField(max_length=50)
    birth_date = models.DateField(null=True)
    phone_number = models.CharField(max_length=100)
    costs = models.IntegerField(default=100)
    role = models.CharField(max_length=15, choices=ROLES)
    profession = models.CharField(max_length=250, choices=PROFESSION, default='Other')
    knowledges = models.TextField(max_length=1000)
    rating = models.FloatField(default=0.0)
    rated = models.IntegerField(default=0)
    hired = models.IntegerField(default=0)
    num_hires = models.IntegerField(default=0)
    photo = models.ImageField(default='default_user.jpg', upload_to='profile_user')

    def __str__(self):
        return f'{ self.user.username } Profile'


class ClientNotifications(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.CharField(max_length=1000)
    url_to_go = models.CharField(max_length=200, default='-')
    date = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    remove = models.BooleanField(default=False)

    def __str__(self):
        return f'{ self.client } notification'


class RepairmanNotifications(models.Model):
    repairman = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.CharField(max_length=1000)
    url_to_go = models.CharField(max_length=200, default='-')
    date = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    remove = models.BooleanField(default=False)

    def __str__(self):
        return f'{ self.repairman } notification'


class UserFavourite(models.Model):
    user = models.IntegerField()
    repairman = models.IntegerField()

    def __str__(self):
        return f'Favorite { self.user }'


class Requests(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=30)
    required_knowledges = models.TextField(max_length=1000)
    price = models.IntegerField()
    address = models.CharField(max_length=30)
    job_description = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(default='default_request.jpg', upload_to='requests_user')
    visible = models.BooleanField(default=True)

    def __str__(self):
        return f'{ self.user.username } Request'

    def get_absolute_url(self):
        return reverse('request_detail', kwargs={'pk': self.pk})


class SeenRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request = models.ForeignKey(Requests, on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f'{ self.user.username } seen { self.request.job_title }'


class Hire(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    repairman = models.IntegerField()
    status = models.CharField(max_length=100, default='pending')
    accepted = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        rep = User.objects.filter(id=self.repairman).first()
        return f'{ self.user.username } hired { rep.username }'


class RepairmanRequests(models.Model):
    repairman = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.IntegerField()
    request_message = models.CharField(max_length=1000, default='No request')
    date = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    done = models.BooleanField(default=False)

    def __str__(self):
        return f'{ self.repairman.username } Request'


class Appliccation(models.Model):
    repairman = models.ForeignKey(User, on_delete=models.CASCADE)
    request = models.ForeignKey(Requests, on_delete=models.CASCADE)


class JobHire(models.Model):
    repairman = models.ForeignKey(User, on_delete=models.CASCADE)
    request = models.ForeignKey(Requests, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, default='pending')
    done = models.BooleanField(default=False)
    date_hired = models.DateTimeField(auto_now_add=True)


class Rate(models.Model):
    repairman = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repairman')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    rate = models.IntegerField()
    feedback = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{ self.repairman.username } rate and feedback'

# https://github.com/furious-luke/django-address --> link za addres fieldove zajedno s google mapsom
