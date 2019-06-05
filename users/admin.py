from django.contrib import admin
from .models import *
from django.urls import path
from django.shortcuts import redirect
import requests
import json

# Register your models here.

admin.site.register(User)
admin.site.register(Post)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'full_name')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    change_list_template = "admin/competition_changelist.html"
    list_display = ('team_num', 'nickname', 'competition_abbreviations')
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('update_FIRST_teams/', self.update_FIRST_teams),
        ]
        return my_urls + urls

    def update_FIRST_teams(self, request):
        data = {
            "size": 100000,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "profile_year": 2019
                            }
                        },
                        {
                            "match": {
                                "team_type": "FRC"
                            }
                        }
                    ]
                }
            },
            "_source": [
                "team_number_yearly",
                "team_nickname",
                "team_type",
                "countryCode",
                "team_postalcode",
                "location",
                "profile_year"
            ]
        }
        url = "http://es01.usfirst.org/teams_v1/_search"
        print("Beginning FIRST Team Import")
        r = requests.request(method='get', url=url, data=json.dumps(data))
        print("Received FIRST Teams.")
        data = r.json()["hits"]["hits"]
        updated = 0
        added = 0
        comp = Competition.objects.get(abbreviation="FRC")
        for team_data in data:
            team_data = team_data["_source"]
            if team_data["team_number_yearly"] > 100000:
                # Yeah, this'll break in a few years for FLL
                # Done to ignore the temporary numbers given by FIRST (aka 2019000065 or whatever)
                # At some point, add the necessary tracking for that (store FIRST's internal team number in here so we
                # can switch it to their real number when they get it)
                continue
            obj, created = Team.objects.update_or_create(
                country=team_data["countryCode"],
                team_num=team_data["team_number_yearly"],
                zip_code=team_data["team_postalcode"],
                lat=team_data["location"][0]["lat"],
                long=team_data["location"][0]["lon"],
                nickname=team_data["team_nickname"],
                competition=comp
            )
            updated += 1
            if created:
                added += 1
        self.message_user(request, "Updated {} teams, added {} teams.".format(updated, added))
        return redirect("../")
