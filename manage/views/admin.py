# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from kinger.models import Group, School, Student, Teacher,ChangeUsername
from manage.forms import ClassForm, ChangeUsernameForm
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from kinger.helpers import get_redir_url
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.sites.models import get_current_site
from django.template.response import TemplateResponse
from kinger.settings import CHANGE_USERNAME_TIMEDELTA
import datetime

@sensitive_post_parameters()
@csrf_protect
#@never_cache
def login(request, template_name='manage/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


@login_required
def change_username(request, template_name="manage/admin_change_username.html"):
    """change user name once"""
    form = ChangeUsernameForm()
    now = datetime.datetime.now()
    #last_time = now + datetime.timedelta(seconds = -CHANGE_USERNAME_TIMEDELTA)
    #change_list = ChangeUsername.objects.filter(user=request.user.id,
                                                #edittime__gt=last_time,edittime__lte=now).order_by('-edittime')
    if has_change(request.user):
        messages.success(request, _(" 只能修改一次"))
    else:
        if request.method == "POST":
            form = ChangeUsernameForm(request.POST)
            if form.is_valid():
                form.save(request.user)
                messages.success(request, _(" Username was changed successfuly"))
                return redirect(get_redir_url(request))
        #else:
            #form = ChangeUsernameForm()

    return render(request, template_name, {'form': form})

def has_change(obj):
    #now = datetime.datetime.now()
    #last_time = now + datetime.timedelta(seconds = -CHANGE_USERNAME_TIMEDELTA)
    change_list = ChangeUsername.objects.filter(user=obj.id)
    return change_list.count()
    
