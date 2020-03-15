from django.db import models
from django.conf import settings
from teams.models import Team, Event


class Post(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=100)
    desc = models.TextField()
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    zip_code = models.CharField(null=True, max_length=10)
    country = models.CharField(null=True, max_length=4)
    lat = models.FloatField(null=True)
    long = models.FloatField(null=True)
    team = models.ForeignKey(Team, models.SET_NULL, related_name="posts", blank=True, null=True)
    event = models.ForeignKey(Event, models.SET_NULL, related_name='posts', blank=True, null=True)


class PostImage(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField()


class PostComment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True
    )
    comment = models.TextField
    posting_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
    )
