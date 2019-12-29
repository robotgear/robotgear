from django.db import models


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


class Event(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.PROTECT)
    key = models.CharField(max_length=16)
    start_date = models.DateField()
    end_date = models.DateField()
    lat = models.FloatField(null=True)
    long = models.FloatField(null=True)