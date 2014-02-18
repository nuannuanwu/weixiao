# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from kinger.helpers import get_redir_url
# from django.shortcuts import render_to_response,render
# from django.template import RequestContext
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.comments import Comment
from django.contrib.comments.views.moderation import perform_delete
from django.contrib.comments.signals import comment_was_posted
from django.contrib import comments
from django.contrib.auth.decorators import login_required, permission_required
# from django.views.decorators.http import require_POST, require_GET

from kinger.models import Tile, TileTag, TileType, Student,Sms, VerifySms
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from django.http import Http404
from django.http import HttpResponse

from kinger import helpers
from django.contrib.auth.models import User
from kinger.profiles.models import Profile

from sms.models import SmsSend,SmsSendAccount

@login_required
def test(request):
	user = request.user
	# sms = SmsSend(tag_id=1,receive_mobile='15814020825',send_mobile='075586329301',content='你好啊',sender=user)
	# sms.save()

	# sms=SmsSend.objects.get(sender=user)
	sms = SmsSendAccount.objects.get(uc='075586329302')

	return HttpResponse(sms.status)







