from django.db import models
from django.conf import settings


class Post(models.Model):
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
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True
    )
