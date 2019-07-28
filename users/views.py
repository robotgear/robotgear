from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, password_validation
from django.core.exceptions import ValidationError
from django.utils.datastructures import MultiValueDictKeyError
from users.models import User, Competition, Team, TeamMembership
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
            return redirect('index')
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
        login(request, user)
        messages.success(request, "Your account has been activated.")
        return redirect('index')
    else:
        messages.error(request, "An error occurred when trying to validate your email. ")
        return render(request, 'index.html')


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
            user.save()
            messages.success(request, "Password changed correctly.")
            return redirect('login')
    else:
        messages.error(request, "An error occurred when trying to validate your email. ")
        return render(request, 'reset.html')


@login_required
def settingsView(request):
    all_competitions = Competition.objects.all()
    own_teams = TeamMembership.objects.filter(user=request.user)
    context = {'competitions': all_competitions, 'teams': own_teams}
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
        # TODO: manual team creation
        return redirect(settingsView)

    membership = TeamMembership()
    membership.user = request.user
    membership.team = team_obj
    membership.relationship = relationship
    membership.save()

    return redirect(f'{reverse("settings")}#teams')


@login_required
def deleteTeamView(request, comp, team):
    membership = TeamMembership.objects.filter(team__competition__abbreviation=comp, team__team_num=team)
    membership.delete()
    return redirect(f'{reverse("settings")}#teams')