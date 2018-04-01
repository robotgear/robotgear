from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Post(models.Model):
	title = models.CharField(max_length=100)
	desc = models.TextField()
	creator = models.ForeignKey(settings.AUTH_USER_MODEL,
	                            on_delete=models.CASCADE)


class User(AbstractUser):
	email_confirmed = models.BooleanField(default=False)