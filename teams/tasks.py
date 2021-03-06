import requests
import json

from django_q.tasks import async_task

from teams.models import Team, Competition

FIRST_PROGRAMS = ['FRC', 'FTC', 'FLL', 'JFLL']


def update_current_year_FIRST(comp=None):
    if comp is None:
        comp = FIRST_PROGRAMS
        for c in comp:
            current_year = Competition.objects.get(abbreviation=c).last_year
            async_task('teams.tasks.update_FIRST_teams', c, current_year)
    else:
        current_year = Competition.objects.get(abbreviation=comp).last_year
        async_task('teams.tasks.update_FIRST_teams', comp, current_year)


def update_all_FIRST():
    print(f"Getting all FIRST teams.")
    data = {
        "size": 1000000,
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
    fetch_FIRST_teams(data)
    print(f"Finished getting all FIRST teams.")


def update_FIRST_teams(comp, year):
    print(f"Getting {comp} teams from {year}")
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
    fetch_FIRST_teams(data)
    print(f"Finished getting {comp} teams from {year}")


def fetch_FIRST_teams(payload):
    url = "https://es02.firstinspires.org/teams_v1/_search"
    r = requests.request(method='get', url=url, data=json.dumps(payload))
    print("Received FIRST Teams.")
    data = r.json()["hits"]["hits"]
    process_FIRST_teams(data)


def process_FIRST_teams(data):
    for team_data in data:
        team_data = team_data["_source"]
        if team_data["team_number_yearly"] > 1000000 or team_data['team_number_yearly'] < 0:
            # Done to ignore the temporary numbers given by FIRST (aka 2019000065 or whatever)
            # At some point, add the necessary tracking for that (store FIRST's internal team number in here so we
            # can switch it to their real number when they get it)
            continue

        try:
            nick = team_data["team_nickname"]
        except KeyError:
            nick = f"Team {team_data['team_number_yearly']}"

        try:
            zip_code = team_data["team_postalcode"]
        except KeyError:
            zip_code = ""

        if not team_data["team_type"] in FIRST_PROGRAMS:
            continue

        try:
            # Get current record for that team from the DB to see if it needs to be updated
            team_get = Team.objects.get(competition=Competition.objects.get(abbreviation=team_data["team_type"]),
                                        team_num=team_data["team_number_yearly"])
        except Team.DoesNotExist:
            # team is new to the DB, create it

            new_team = Team(competition=Competition.objects.get(abbreviation=team_data["team_type"]),
                            team_num=team_data["team_number_yearly"],
                            zip_code=zip_code,
                            country=team_data["countryCode"],
                            lat=team_data["location"][0]["lat"],
                            long=team_data["location"][0]["lon"],
                            nickname=nick,
                            last_year_competing=team_data["profile_year"],
                            added_manually=False
                            )
            new_team.save()
            continue

        if team_get.last_year_competing <= team_data["profile_year"]:
            # if the recorded last year is less than or equal to the gotten year, update the team
            team_get.zip_code = zip_code
            team_get.country = team_data["countryCode"]
            team_get.lat = team_data["location"][0]["lat"]
            team_get.long = team_data["location"][0]["lon"]
            team_get.nickname = nick
            team_get.last_year_competing = team_data["profile_year"]
            team_get.save()
