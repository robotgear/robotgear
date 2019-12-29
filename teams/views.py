from django.db import IntegrityError
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from teams.models import Team, Competition
from users.models import TeamMembership

from datetime import datetime


@login_required
@require_POST
def add_team_view(request):
    competition = request.POST.get('competition')
    team_num = request.POST.get('team_num')
    relationship = request.POST.get('relationship')
    try:
        team_obj = Team.objects.filter(competition__abbreviation=competition).get(team_num=team_num)
    except Team.DoesNotExist:
        current_year = datetime.now().year
        context = {'competition': competition, 'team_num': team_num, 'relationship': relationship,
                   'years': list(range(current_year+1, 1980, -1)), 'hide_relationship': False}
        return render(request, 'new_team.html', context=context)

    membership = TeamMembership()
    membership.user = request.user
    membership.team = team_obj
    membership.relationship = relationship
    try:
        membership.save()
    except IntegrityError:
        messages.error(request, "You are already associated with that team. Edit your relationship if you'd like to add"
                                " more than one role.")

    return redirect(f'{reverse("settings")}#teams')


@login_required
@require_POST
def new_team_view(request):
    competition = request.POST.get('competition')
    comp_obj = Competition.objects.get(abbreviation=competition)
    team_num = request.POST.get('team_num')

    nickname = request.POST.get('nickname')
    zip_code = request.POST.get('zip_code')
    country = request.POST.get('country')
    last_year = request.POST.get('last_year')
    try:
        team = Team.objects.create(competition=comp_obj,
                                   team_num=team_num,
                                   nickname=nickname,
                                   zip_code=zip_code,
                                   country=country,
                                   last_year_competing=last_year,
                                   added_manually=True)
    except IntegrityError:
        team = Team.objects.get(competition__abbreviation=competition,
                                team_num=team_num)
        team.nickname = nickname
        team.zip_code = zip_code
        team.country = country
        team.last_year_competing = last_year
    team.save()

    relationship = request.POST.get('relationship')
    if relationship != "" and relationship is not None:
        membership = TeamMembership()
        membership.user = request.user
        membership.team = team
        membership.relationship = relationship
        membership.save()
    return redirect(f'{reverse("settings")}#teams')


@login_required
def delete_team_view(request, comp, team):
    membership = TeamMembership.objects.get(team__competition__abbreviation=comp,
                                            team__team_num=team,
                                            user=request.user)
    membership.delete()
    return redirect(f'{reverse("settings")}#teams')


@login_required
def edit_team_view(request, comp, team):
    if request.method == "GET":
        team = Team.objects.get(team_num=team, competition__abbreviation=comp)
        current_year = datetime.now().year
        context = {'competition': team.competition.abbreviation,
                   'team_num': team.team_num,
                   'relationship': "",
                   'nickname': team.nickname,
                   'zip_code': team.zip_code,
                   'country': team.country,
                   'selected_year': team.last_year_competing,
                   'hide_relationship': True,
                   'years': list(range(current_year+1, 1980, -1))}
        return render(request, 'new_team.html', context=context)


def team_detail(request, comp, team):
    team = get_object_or_404(Team, team_num=team, competition__abbreviation=comp)
    return render(request, 'team_detail.html', context={'team': team})
