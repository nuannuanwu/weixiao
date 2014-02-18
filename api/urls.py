# -*- coding: utf-8 -*-

"""
| api 路由.
| 所有的路由的调用方法和返回接口请查看 `接口文档 <http://192.168.1.222:8080/API%E6%96%87%E6%A1%A3>`_
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('api.views',
    url(r'^users/show/$', "users"),
    url(r'^account/set_device_token/$', "devices"),

    url(r'^account/get_uid/$', "accounts", {"method": "get_uid"}),
    url(r'^account/profile/class_list/$', "groups", {"method": "list"}),
    url(r'^account/profile/identity/$', "accounts", {"method": "identity"}),
    url(r'^account/change_password/$', "accounts", {"method": "change_password"}),
    url(r'^account/change_avatar/$', "accounts", {"method": "change_avatar"}),
    url(r'^account/access_log/$', "accounts", {"method": "access_log"}),
    
    url(r'^actives/$', "actives"),
    url(r'^actives/show/$', "actives"),
    url(r'^actives/create/$', "actives_actions", {"method": "post"}),
    url(r'^actives/modify/$', "actives_actions", {"method": "modify"}),
    url(r'^actives/destroy/$', "actives_actions", {"method": "delete"}),
    
    url(r'^cookbooks/$', "cookbooks"),
    url(r'^cookbooks/show/$', "cookbooks"),

    url(r'^tiles/$', "tiles"),
    url(r'^tiles/show/$', "tiles"),
    url(r'^tiles/create/$', "tiles_actions", {"method": "post"}),
    url(r'^tiles/modify/$', "tiles_actions", {"method": "modify"}),
    url(r'^tiles/destroy/$', "tiles_actions", {"method": "delete"}),
    url(r'^tiles/upload_video/$', "tiles_actions", {"method": "upload_video"}),

    url(r'^tiles/tags/$', "tiles_tags"),
    url(r'^tiles/types/$', "tiles_types"),
    url(r'^tiles/like/$', "tiles_likeable", {"method": "post"}, name="api_tiles_like"),
    
    # 给 web 端使用的特殊接口. 对提交进行 ``csrf`` 保护(防止跨域提交).
    url(r'^web/tiles/like/$', "web_tiles_likeable", {"method": "post"}, name="api_web_tiles_like"),
    url(r'^tiles/by_babys/$', "tiles_category", {"category": "for_baby"}),
    url(r'^tiles/by_tags/$', "tiles_category", {"category": "by_tags"}),
    url(r'^tiles/by_babys_with_push/$', "tiles_category", {"category": "for_baby_with_promotion"}),
    url(r'^tiles/get_event_setting/$', "event_setting"),

    url(r'^tiles/get_event_setting/$', "tiles_event"),

    # 瓦片分类的
    url(r'^tiles/categorys/$', "tiles_categorys", {"method":"parent_category"}),
    url(r'^tiles/categorys/subcategory$', "tiles_categorys", {"method":"sub_category"}),
    
    url(r'^tiles/check_create_tag/$', "tiles_create_tags"),

    url(r'^comments/show/$', "comments"),
    url(r'^comments/create/$', "comments", {"method": "post"}),
    url(r'^web/comments/create/$', "web_comments", {"method": "post"}, name="api_web_comments_create"),
    url(r'^comments/destroy/$', "comments", {"method": "delete"}),

    url(r'^comments/templater/types/$', "comments_templater_types"),
    url(r'^comments/templater/$', "comments_templater"),


    url(r'^students/show/$', "students"),
    url(r'^students/by_class/$', "students_category", {"category": "by_class"}),

    url(r'^teachers/show/$', "teachers"),
    url(r'^teachers/by_class/$', "teachers_category", {"category": "by_class"}),

    url(r'^messages/contacts/$', "messages", {"method": "contacts"}),
    url(r'^messages/history2/$', "messages", {"method": "history"}),
    url(r'^messages/history/$', "messages_test"),
    url(r'^messages/history_to_class/$', "mesage_to_class"),
    
    
    url(r'^messages/create/$', "messages_actions", {"method": "post"}),
    url(r'^messages/create_to_class/$', "messages_actions", {"method": "post_to_class"}),
    url(r'^messages/destroy/$', "messages_actions", {"method": "delete"}),

    url(r'^remind/unread_count/$', "messages", {"method": "unread_count"},name="api_web_unread_count"),

    url(r'^not_found/$', "api_not_found", name="api_not_found"),

)
