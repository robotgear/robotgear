from django.db import models
from django.conf import settings

# Create your models here.

class Post(models.Model):
	title = models.CharField(max_length=100)
	desc = models.TextField()
	creator = models.ForeignKey(settings.AUTH_USER_MODEL,
	                            on_delete=models.CASCADE)

