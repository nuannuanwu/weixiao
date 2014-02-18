# -*- coding: utf-8 -*-
# import the logging library
import logging
import datetime

# Get an instance of a logger
logger = logging.getLogger(__name__)

from piston.handler import BaseHandler
from api.helpers import rc,media_path
from kinger.models import Group, EventType, Cookbook
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


class EventSettingHandler(BaseHandler):
    allowed_methods = ("GET",)
    model = EventType
    fields = ("type_id", "name", "content", "img")

    @classmethod
    def type_id(cls, model, request):
        return model.id

    @classmethod
    def img(cls, model, request):
        try:
            url = model.img
            url = media_path(url,"normal")
            return url
            #return model.img.url
        except Exception, e:
            # FIXME: return the defualt image
            logger.warning(e)
            return ""

    def _get_cookbook_settings(self, qs, school, c_group, group=1):
        """
        如果有食谱发布，读取食谱（有班级读班级的,继承关系），没有读取自eventsetting
        """       
        is_pub = False
        date = datetime.date.today() + datetime.timedelta(days=1)

        types = EventType.objects.filter(group=group)
        new_types = []

        ck = Cookbook.objects.get_cookbook_date(group=c_group, school=school, date=date)
        ck_items = Cookbook.objects.get_items()

        for i in ck_items:
            if ck['con'][i]['con']:                
                is_pub = True
                break

        if is_pub:                    
            for el in types.all():
                print el.name
                if el.name == u'早餐':
                    el.content = ck['con']['breakfast']['con']
                elif el.name == u'早点':
                    el.content = ck['con']['light_breakfast']['con']
                elif el.name == u'午餐':
                    el.content = ck['con']['lunch']['con']
                elif el.name == u'午点':
                    el.content = ck['con']['light_lunch']['con']
                elif el.name == u'晚餐':
                    el.content = ck['con']['dinner']['con']
                elif el.name == u'晚点':
                    el.content = ck['con']['light_dinner']['con']
                else:
                    el.content = ''

                new_types.append(el)
        else:       
            for el in types.all():
                try:
                    el.content = el.settings.filter(qs).latest("id").content
                except ObjectDoesNotExist:
                    el.content = ""
                    pass
                new_types.append(el)
        return new_types

    def _get_settings(self, group, qs):
        """
        返回学校今日活动预设。
        """
        types = EventType.objects.filter(group=group)
        new_types = []
        for el in types.all():
            try:
                el.content = el.settings.filter(qs).latest("id").content
            except ObjectDoesNotExist:
                el.content = ""
                pass
            new_types.append(el)
        return new_types

    def read(self, request):
        class_id = request.GET.get("class_id")
        if not class_id:
            return rc.BAD_REQUEST

        try:
            group = Group.objects.get(pk=class_id)
        except Group.DoesNotExist:           
            return rc.NOT_HERE

        school = group.school

        # FIXME: school__pk == 0 is default settings.
        # but there are no school's pk is 0, no default settings yet.
        q = Q(school=group.school) or Q(school__pk=0)

        event_settings = self._get_settings(0, q)
        cookbook_settings = self._get_cookbook_settings(qs=q, school=school, c_group=group)

        return {"events": event_settings, "cookbooks": cookbook_settings}
