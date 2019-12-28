from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, password_validation
from django.core.exceptions import ValidationError
from django.utils.datastructures import MultiValueDictKeyError
from users.models import User, Competition, Team, TeamMembership
from users.forms import UserDescriptionForm, UserAvatarForm
from django.contrib import messages
from django.db import IntegrityError
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from users.tokens import account_activation_token
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic.base import TemplateView
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from datetime import datetime
from django.views.generic import DetailView


# Create your views here.


class TermsAndConditions(TemplateView):
    template_name = "terms_and_conditions.html"


class IndexView(TemplateView):
    template_name = "index.html"


def loginView(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.email_confirmed:
                messages.error(request, 'Please confirm your email before logging in. You can resend the confirmation'
                                        f' email <a href="{reverse("reactivate", kwargs={"username":username})}">here.</a>',
                               extra_tags='safe')
                return render(request, 'login.html')
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Incorrect login details.")
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def logoutView(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('index')
    else:
        return redirect(loginView)


def registerView(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        try:
            password_validation.validate_password(password)
        except ValidationError:
            messages.error(request, "Invalid password.")
            return render(request, 'register.html')

        try:
            user = User.objects.create_user(username, email, password)

        except IntegrityError:
            messages.error(request, "That username is taken.")
            return render(request, 'register.html')

        if user is not None:
            current_site = get_current_site(request)
            subject = 'Activate Your RobotGear Account'
            message = render_to_string('email/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': force_text(urlsafe_base64_encode(force_bytes(user.pk))),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            messages.success(request, "Your account has been created. Please check your email.")
            return redirect('login')
        else:
            messages.error(request, "An error has occurred, please try again.")
            return render(request, 'register.html')
    else:
        return render(request, 'register.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        messages.success(request, "Your account has been activated.")
        return redirect('login')
    else:
        messages.error(request, "An error occurred when trying to validate your email. ")
        return render(request, 'index.html')


def reactivate(request, username):
    user = User.objects.get(username=username)
    if user is not None:
        current_site = get_current_site(request)
        subject = 'Activate Your RobotGear Account'
        message = render_to_string('email/activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': force_text(urlsafe_base64_encode(force_bytes(user.pk))),
            'token': account_activation_token.make_token(user),
        })
        user.email_user(subject, message)
        messages.success(request, "An activation email has been resent to your email on file.")
        return redirect('login')
    else:
        messages.error(request, "No user with that username found.")
        return render(request, 'register.html')


def resetView(request):
    if request.user.is_authenticated:
        return redirect(request, 'index')
    if request.method == "GET":
        return render(request, 'reset.html')
    username = request.POST.get('username')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, "That user does not exist.")
        return render(request, 'reset.html')
    current_site = get_current_site(request)
    subject = 'Reset Your RobotGear Password'
    message = render_to_string('reset_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': force_text(urlsafe_base64_encode(force_bytes(user.pk))),
        'token': default_token_generator.make_token(user),
    })
    user.email_user(subject, message)
    messages.success(request, "A link has been sent to you. Please check your email.")
    return render(request, 'reset.html')


def resetLinkView(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "GET":
            return render(request, 'email/reset_pass_entry.html', context={'username': user.username})
        elif request.method == "POST":
            password = request.POST.get("password")
            try:
                password_validation.validate_password(password)
            except ValidationError:
                messages.error(request, "Invalid password.")
                return render(request, 'email/reset_pass_entry.html')
            user.set_password(password)
            user.email_confirmed = True
            user.save()
            messages.success(request, "Password changed correctly.")
            return redirect('login')
    else:
        messages.error(request, "An error occurred when trying to validate your email. ")
        return render(request, 'reset.html')


@login_required
@require_POST
def changeUsernameView(request):
    try:
        username = request.POST.get('username')
        username = request.user.normalize_username(username)
        request.user.username = username
        request.user.save()
        messages.success(request, 'Successfully updated your username.')
    except IntegrityError:
        messages.error(request, "That username is taken.")
    return redirect('settings')


@login_required
def settingsView(request):
    all_competitions = Competition.objects.all()
    own_teams = TeamMembership.objects.filter(user=request.user).order_by('team__competition__abbreviation','team__team_num')
    desc_form = UserDescriptionForm(initial={'description': request.user.description})
    avatar_form = UserAvatarForm()
    context = {'competitions': all_competitions,
               'teams': own_teams,
               'desc_form': desc_form,
               'avatar_form':avatar_form}
    return render(request, 'settings.html', context=context)


def resetLoggedInView(request):
    if request.user.is_authenticated:
        current_site = get_current_site(request)
        subject = 'Reset Your RobotGear Password'
        message = render_to_string('reset_email.html', {
            'user': request.user,
            'domain': current_site.domain,
            'uid': force_text(urlsafe_base64_encode(force_bytes(request.user.pk))),
            'token': default_token_generator.make_token(request.user),
        })
        request.user.email_user(subject, message)
        messages.success(request, "A link has been sent to you. Please check your email.")
        return redirect('settings')
    else:
        return redirect(loginView)


def changeEmailView(request):
    if request.user.is_authenticated:
        if request.method != "POST":
            return redirect('settings')
        try:
            new_email = request.POST.get("email")
        except MultiValueDictKeyError:
            new_email = request.user.email
        request.user.email_confirmed = False
        request.user.email = new_email
        request.user.save()
        current_site = get_current_site(request)
        subject = 'Activate Your RobotGear Account'
        message = render_to_string('email/activation_email.html', {
            'user': request.user,
            'domain': current_site.domain,
            'uid': force_text(urlsafe_base64_encode(force_bytes(request.user.pk))),
            'token': account_activation_token.make_token(request.user),
        })
        request.user.email_user(subject, message)
        messages.success(request, "Your account has been created. Please check your email.")
        return redirect('settings')
    else:
        return redirect(loginView)


@login_required
@require_POST
def addTeamView(request):
    competition = request.POST.get('competition')
    team_num = request.POST.get('team_num')
    relationship = request.POST.get('relationship')
    try:
        team_obj = Team.objects.filter(competition__abbreviation=competition).get(team_num=team_num)
    except Team.DoesNotExist:
        current_year = datetime.now().year
        context = {'competition': competition, 'team_num': team_num, 'relationship': relationship,
                   'years': list(range(current_year+1, 1980, -1)),'hide_relationship': False}
        return render(request, 'new_team.html', context=context)

    membership = TeamMembership()
    membership.user = request.user
    membership.team = team_obj
    membership.relationship = relationship
    try:
        membership.save()
    except IntegrityError:
        messages.error(request, "You are already associated with that team. Edit your relationship if you'd like to add more than one role.")

    return redirect(f'{reverse("settings")}#teams')


@login_required
@require_POST
def newTeamView(request):
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
def deleteTeamView(request, comp, team):
    membership = TeamMembership.objects.get(team__competition__abbreviation=comp, team__team_num=team, user=request.user)
    membership.delete()
    return redirect(f'{reverse("settings")}#teams')


@login_required
@require_POST
def editRelationshipView(request):
    relationship = request.POST.get('relationship')
    competition = request.POST.get('competition')
    team_num = request.POST.get('team_num')

    membership = TeamMembership.objects.get(team__competition__abbreviation=competition, team__team_num=team_num)
    membership.relationship = relationship
    membership.save()

    return redirect(f'{reverse("settings")}#teams')

@login_required
def editTeamView(request, comp, team):
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


def userDetail(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'user_detail.html', context={'user_profile': user})


def teamDetail(request, comp, team):
    team = get_object_or_404(Team, team_num=team, competition__abbreviation=comp)
    return render(request, 'team_detail.html', context={'team': team})


@login_required
@require_POST
def updateDesc(request):
    form = UserDescriptionForm(request.POST)

    if form.is_valid():
        request.user.description = form.cleaned_data['description']
        request.user.save()
        messages.success(request, "Your description has been updated.")
        return redirect(f'{reverse("settings")}#profile')


@login_required
@require_POST
def uploadAvatar(request):
    form = UserAvatarForm(request.POST, request.FILES)
    if form.is_valid():
        user = request.user
        user.avatar = request.FILES['avatar']
        user.save()
        messages.success(request, "Your avatar has been updated.")
        return redirect(f'{reverse("settings")}#profile')
    else:
        messages.error(request, "Error uploading avatar.")
        return redirect(f'{reverse("settings")}#profile')
