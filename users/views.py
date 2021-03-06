from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, password_validation
from django.core.exceptions import ValidationError
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages
from django.db import IntegrityError
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from users.models import User,  TeamMembership
from teams.models import Competition
from users.forms import UserDescriptionForm, UserAvatarForm
from users.tokens import account_activation_token


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.email_confirmed:
                messages.error(request, 'Please confirm your email before logging in. You can resend the confirmation'
                                        f' email <a href="{reverse("reactivate", kwargs={"username":username})}">here.'
                                        f'</a>',
                               extra_tags='safe')
                return render(request, 'login.html')
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Incorrect login details.")
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('index')
    else:
        return redirect(login_view)


def register_view(request):
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
            send_activation_email(request, user)
            messages.success(request, "Your account has been created. Please check your email.")
            return redirect('login')
        else:
            messages.error(request, "An error has occurred, please try again.")
            return render(request, 'register.html')
    else:
        return render(request, 'register.html')


def send_activation_email(request, user):
    current_site = get_current_site(request)
    subject = 'Activate Your RobotGear Account'
    message = render_to_string('email/activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': force_text(urlsafe_base64_encode(force_bytes(user.pk))),
        'token': account_activation_token.make_token(user),
    })
    user.email_user(subject, message)


def activate_view(request, uidb64, token):
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


def reactivate_view(request, username):
    user = User.objects.get(username=username)
    if user is not None:
        send_activation_email(request, user)
        messages.success(request, "An activation email has been resent to your email on file.")
        return redirect('login')
    else:
        messages.error(request, "No user with that username found.")
        return render(request, 'register.html')


def reset_view(request):
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


def reset_link_view(request, uidb64, token):
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
def change_username_view(request):
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
def settings_view(request):
    all_competitions = Competition.objects.all()
    own_teams = TeamMembership.objects.filter(user=request.user)\
        .order_by('team__competition__abbreviation', 'team__team_num')
    desc_form = UserDescriptionForm(initial={'description': request.user.description})
    avatar_form = UserAvatarForm()
    context = {'competitions': all_competitions,
               'teams': own_teams,
               'desc_form': desc_form,
               'avatar_form': avatar_form}
    return render(request, 'settings.html', context=context)


def reset_logged_in_view(request):
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
        return redirect(login_view)


def change_email_view(request):
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
        return redirect(login_view)


@login_required
@require_POST
def edit_relationship_view(request):
    relationship = request.POST.get('relationship')
    competition = request.POST.get('competition')
    team_num = request.POST.get('team_num')

    membership = TeamMembership.objects.get(team__competition__abbreviation=competition, team__team_num=team_num)
    membership.relationship = relationship
    membership.save()

    return redirect(f'{reverse("settings")}#teams')


def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'user_detail.html', context={'user_profile': user})


@login_required
@require_POST
def update_desc(request):
    form = UserDescriptionForm(request.POST)

    if form.is_valid():
        request.user.description = form.cleaned_data['description']
        request.user.save()
        messages.success(request, "Your description has been updated.")
        return redirect(f'{reverse("settings")}#profile')


@login_required
@require_POST
def upload_avatar(request):
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
