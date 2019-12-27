from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class Competition(models.Model):
    abbreviation = models.CharField(max_length=4)
    full_name = models.CharField(max_length=120)
    link = models.URLField()
    auto_import = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class Team(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.PROTECT)
    nickname = models.CharField(max_length=100, null=True)
    team_num = models.CharField(max_length=5,
                                null=True
                                # set so database migrations won't complain, should never be truly null in the DB
                                )  # set to CharField to support VEX
    zip_code = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=4)
    lat = models.FloatField(null=True)
    long = models.FloatField(null=True)
    last_year_competing = models.PositiveSmallIntegerField(null=True)
    added_manually = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['team_num', 'competition'], name="unique_team")
        ]
        ordering = ['team_num', 'competition']

    def team_name_w_comp(self):
        return "{}{}".format(self.competition.abbreviation, self.team_num)

    team_name_w_comp.short_description = 'Team Number'

    def __str__(self):
        return "{}{}".format(self.competition.abbreviation, self.team_num)


class User(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    teams = models.ManyToManyField(Team, through='TeamMembership', related_name='users')
    zip_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=4, blank=True)
    description = models.CharField(max_length=400, blank=True)


class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=50)

    class Meta:
        unique_together = ['user', 'team']
        ordering = ['team__competition__abbreviation', 'team__team_num']


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    link = models.URLField()


class Event(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.PROTECT)
    key = models.CharField(max_length=16)
    start_date = models.DateField()
    end_date = models.DateField()
    lat = models.FloatField(null=True)
    long = models.FloatField(null=True)


class Manufacturer(models.Model):
    name = models.CharField(max_length=120)
    url = models.URLField()


class Product(models.Model):
    product_key = models.CharField(max_length=16)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
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
    zip_code = models.CharField(null=True, max_length=10)
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
        null=True
    )
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True
    )
