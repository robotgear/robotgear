from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Post(models.Model):
	title = models.CharField(max_length=100)
	desc = models.TextField()
	creator = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True
	)


class PostImage(models.Model):
	post = models.ForeignKey(
		Post,
		on_delete=models.CASCADE
	)
	image = models.ImageField()



class Team(models.Model):
	competition = models.CharField(
		choices=(
			("FRC", "FIRST Robotics Competition"),
			("FTC", "FIRST Tech Challenge"),
			("FLL", "FIRST Lego League"),
			("JFLL", "Junior FIRST Lego League"),
			("VRC", "VEX Robotics Competition"),
			("VIQ", "VEX IQ Challenge"),
			("BEST", "BEST")
		),
		max_length=4
	)
	team_num = models.CharField(max_length=5,
		null=True  # set so database migrations won't complain, should never be truly null in the DB
	)  # set to CharField to support VEX


class User(AbstractUser):
	email_confirmed = models.BooleanField(default=False)
	teams = models.ManyToManyField(Team)