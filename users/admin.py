from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.urls import path
from django.shortcuts import redirect
import requests
import json

# Register your models here.


class MembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 0
    raw_id_fields = ("team", )


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Custom Entries', {'fields': ('email_confirmed', 'zip_code', 'country',
                                                                      'description', 'avatar')}),)
    inlines = [MembershipInline]
    exclude = ('teams',)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'full_name')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    change_list_template = "admin/competition_changelist.html"
    list_display = ('team_name_w_comp', 'nickname')
    search_fields = ('team_num', 'nickname')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('update/<str:comp>/', self.update)
        ]
        return my_urls + urls

    def update(self, request, comp):
        if comp == "all":
            data = {
                "size": 100000,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "team_type": comp
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
            url = "https://es02.firstinspires.org/teams_v1/_search"
            print("Beginning FIRST Team Import")
            r = requests.request(method='get', url=url, data=json.dumps(data))
            print("Received FIRST Teams.")
            data = r.json()["hits"]["hits"]
            updated = 0
            added = 0
            for team_data in data:
                team_data = team_data["_source"]
                if team_data["team_number_yearly"] > 100000:
                    # Yeah, this'll break in a few years for FLL
                    # Done to ignore the temporary numbers given by FIRST (aka 2019000065 or whatever)
                    # At some point, add the necessary tracking for that (store FIRST's internal team number in here so
                    # we can switch it to their real number when they get it)
                    continue

                obj, created = Team.objects.update_or_create(
                    competition=Competition.objects.get(abbreviation=team_data["team_type"]),
                    team_num=team_data["team_number_yearly"],
                    defaults={
                        "zip_code": team_data["team_postalcode"],
                        "country": team_data["countryCode"],
                        "lat": team_data["location"][0]["lat"],
                        "long": team_data["location"][0]["lon"],
                        "nickname": team_data["team_nickname"],
                        "last_year_competing": team_data["profile_year"]
                    }
                )
                updated += 1
                if created:
                    added += 1
            self.message_user(request, "Updated {} teams, added {} teams.".format(updated, added))
            return redirect("admin:users_team_changelist")
        else:
            updated, added = self.update_FIRST_teams(comp, 2019)
            self.message_user(request, "Updated {} teams, added {} teams.".format(updated, added))
            return redirect("admin:users_team_changelist")

    def update_FIRST_teams(self, comp, year, current=False):
        data = {
            "size": 100000,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "profile_year": year
                            }
                        },
                        {
                            "match": {
                                "team_type": comp
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
        url = "https://es02.firstinspires.org/teams_v1/_search"
        print("Beginning FIRST Team Import")
        r = requests.request(method='get', url=url, data=json.dumps(data))
        print("Received FIRST Teams.")
        data = r.json()["hits"]["hits"]
        updated = 0
        added = 0
        for team_data in data:
            team_data = team_data["_source"]
            if team_data["team_number_yearly"] > 100000:
                # Yeah, this'll break in a few years for FLL
                # Done to ignore the temporary numbers given by FIRST (aka 2019000065 or whatever)
                # At some point, add the necessary tracking for that (store FIRST's internal team number in here so we
                # can switch it to their real number when they get it)
                continue
            obj, created = Team.objects.update_or_create(
                competition=Competition.objects.get(abbreviation=team_data["team_type"]),
                team_num=team_data["team_number_yearly"],
                defaults={
                    "zip_code": team_data["team_postalcode"],
                    "country": team_data["countryCode"],
                    "lat": team_data["location"][0]["lat"],
                    "long": team_data["location"][0]["lon"],
                    "nickname": team_data["team_nickname"],
                    "last_year_competing": team_data["profile_year"]
                }
            )
            if current:
                obj.nickname = team_data["team_nickname"]
                obj.save()
            updated += 1
            if created:
                added += 1
        return updated, added
