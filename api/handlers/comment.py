# -*- coding: utf-8 -*-

from piston.handler import BaseHandler
from api.helpers import rc, DispatchMixin
from django.db.models import Q
from django.conf import settings
from django.contrib.comments import signals

from django.contrib.comments import Comment
from django.contrib.comments.views.moderation import perform_delete
from django.contrib import comments
from django.contrib.contenttypes.models import ContentType
from api.helpers import query_range_filter

import api.handlers.user
from kinger.models import CommentTemplaterType,CommentTemplater,Tile


class CommentHandler(DispatchMixin, BaseHandler):
    """
    Api for comments resource
    """
    model = Comment
    fields = ("id", "comment", "submit_date", ("user", ()))

    allowed_methods = ("GET", "POST")
    csrf_exempt = True

    def get(self, request):
        """
        获得某条瓦片的评论详细信息

        ``GET`` `comments/show/ <http://192.168.1.222:8080/v1/comments/show>`_

        :param tid:
            瓦片 id.

        :param comment_id:
            某条评论的 id
        """
        params = request.GET

        # single one
        comment_id = params.get("comment_id")
        if comment_id:
            try:
                return Comment.objects.get(pk=comment_id, is_removed=False, is_public=True)
            except Comment.DoesNotExist:
                return rc.NOT_HERE

        # all
        tid = params.get("tid")
        try:
            from kinger.helpers import add_daily_record_visitor
            tile = Tile.objects.get(id=tid)
            add_daily_record_visitor(request.user,tile)
        except:
            pass
        ct = ContentType.objects.get_by_natural_key("kinger", "tile")
        queryset = Comment.objects.filter(object_pk=tid, content_type=ct) \
            .filter(is_removed=False, is_public=True).order_by("-submit_date")

        return query_range_filter(params, queryset, "comments")

    @DispatchMixin.post_required
    def post(self, request):
        """
        发布一条评论

        ``POST`` `comments/create/ <http://192.168.1.222:8080/v1/comments/create>`_

        :param tid:
            评论对象(瓦片)的 id.

        :param content:
            评论内容
        """
        params = request.POST.copy()

        tid = params.get("tid")

        if not params.get('name', ''):
            params["name"] = request.user.get_full_name() or request.user.username
        if not params.get('email', ''):
            params["email"] = request.user.email

        try:
            ct = ContentType.objects.get_by_natural_key("kinger", "tile")
        except ContentType.DoesNotExist:
            return rc.NOT_HERE
        comment = Comment(object_pk=tid, content_type=ct, site_id=settings.SITE_ID)
        comment.comment = params.get("content")
        comment.user_name = params.get("name")
        comment.email = params.get("email")
        comment.ip_address = request.META.get("REMOTE_ADDR", None)

        if request.user.is_authenticated():
            comment.user = request.user

        # Signal that the comment is about to be saved
        responses = signals.comment_will_be_posted.send(
            sender=comment.__class__,
            comment=comment,
            request=request
        )

        for (receiver, response) in responses:
            if response == False:
                return rc.BAD_REQUEST
                # return CommentPostBadRequest(
                #     "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

        # Save the comment and signal that it was saved
        comment.save()
        print signals.comment_was_posted.send(
            sender=comment.__class__,
            comment=comment,
            request=request
        ),'signals----------------------------------------------------'

        return comment

    @DispatchMixin.post_required
    def delete(self, request):
        """
        删除一条评论

        ``POST`` `comments/destroy <http://192.168.1.222:8080/v1/comments/create>`_

        :param id:
            某条评论的 id.
        """
        comment_id = request.POST.get("id")
        try:
            klass = comments.get_model()
            comment = klass.objects.get(pk=comment_id, site__pk=settings.SITE_ID, is_removed=False)
        except klass.DoesNotExist:
            return rc.NOT_HERE

        if request.user == comment.user:
            perform_delete(request, comment)
            comment.content_object.after_del_comments()
            return rc.accepted({"result": True})
        else:
            return rc.FORBIDDEN


class CommentTemplaterHandler(DispatchMixin, BaseHandler):
    """
    Api for comments resource
    """
    model = CommentTemplater

    fields = ('id', 'content', 'type_id')

    allowed_methods = ("GET")
    csrf_exempt = True

    def read(self, request):
        params = request.GET
        type_id = params.get("type_id")

        q = Q()
        if type_id:
            try:
                type = CommentTemplaterType.objects.get(pk=type_id)
                q = Q(type__pk=type_id)
            except CommentTemplaterType.DoesNotExist:
                return rc.NOT_HERE

        queryset = CommentTemplater.objects.filter(q)
        return query_range_filter(params, queryset, "templaters")


class CommentTemplaterTypeHandler(BaseHandler):
    """
    api for *Tile* resource
    """
    model = CommentTemplaterType
    fields = ("type_id", "name")
    allowed_methods = ("GET",)

    @classmethod
    def type_id(cls, model, request):
        return model.id

    def read(self, request):
        qs = CommentTemplaterType.objects.all()
        return query_range_filter(request.GET, qs, "types")
