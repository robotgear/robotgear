from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.


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
	),  # set to CharField to support VEX
	zip_code = models.CharField(null=True, max_length=10)
	country = models.CharField(null=True, max_length=4)
	lat = models.FloatField(null=True)
	long = models.FloatField(null=True)
	stock = models.ManyToManyField('product')


class User(AbstractUser):
	email_confirmed = models.BooleanField(default=False)
	teams = models.ManyToManyField(Team)
	zip_code = models.CharField(null=True, max_length=10)
	country = models.CharField(null=True, max_length=4)


class Event(models.Model):
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
	key = models.CharField(max_length=16)
	start_date = models.DateField()
	end_date = models.DateField()
	lat = models.FloatField(null=True)
	long = models.FloatField(null=True)


class Product(models.Model):
	product_key = models.CharField(max_length=16)
	manufacturer = models.CharField(
		choices=(
			("VEX", "VEX Robotics"),
			("AM", "AndyMark"),
			("REV", "REV Robotics"),
			("CTR", "Cross the Road Electronics"),
			("RPR", "RoboPromo"),
			("RSH", "RobotShop"),
			("WCP", "West Coast Products"),
			("MCM", "McMaster Carr")
		),
		max_length=3
	)
	identical = models.ManyToManyField('self')
	similar = models.ManyToManyField('self')


class Post(models.Model):
	title = models.CharField(max_length=100)
	desc = models.TextField()
	creator = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True
	)
	zip_code = models.CharField(null=True,max_length=10)
	country = models.CharField(null=True, max_length=4)
	lat = models.FloatField(null=True)
	long = models.FloatField(null=True)
	events = models.ManyToManyField(Event)
	products = models.ManyToManyField('product')


class PostImage(models.Model):
	post = models.ForeignKey(
		Post,
		on_delete=models.CASCADE
	)
	image = models.ImageField()


class PostComment(models.Model):
	post = models.ForeignKey(
		Post,
		on_delete=models.CASCADE
	)
	comment = models.TextField
	posting_user = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null = True
	)
	parent_comment = models.ForeignKey(
		'self',
		on_delete=models.SET_NULL,
		null = True
	)