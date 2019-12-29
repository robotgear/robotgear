from django.db import models
from django.contrib.auth.models import AbstractUser
from teams.models import Team


class User(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    teams = models.ManyToManyField(Team, through='TeamMembership', related_name='users')
    zip_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=4, blank=True)
    description = models.TextField(blank=True)
    avatar = models.ImageField(blank=True)


class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=50)

    class Meta:
        unique_together = ['user', 'team']
        ordering = ['team__competition__abbreviation', 'team__team_num']
