# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.core.cache import cache

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from kinger import settings
from kinger.forms import KSignupForm, KChangeEmailForm, KEditProfileForm, KAuthenticationForm


# handler404 = "kinger.views.errors.handler404"
handler500 = "kinger.views.errors.handler500"

urlpatterns = patterns("kinger.views.frontend",
        url('^index/$', "index", name="home"),
        url('^cal/$', "cal", name="kinger_cal"),
#        url('^axis/$', "time_axis", name="kinger_time_axis"),
#        url('^test/$', "test", name="kinger_test"),
        url(r'^pre/$', "index", name='home'),
        url('^tile/(?P<tile_id>\d+)/$', "view", name='tile_view'),
        url('^tile/comment/(?P<comment_id>\d+)/delete/$', "delete_comment", name='tile_delete_comment'),
        url(r'^get_user_info/$', "get_user_info", name="kinger_get_user_info"), 
        url(r'^vcar/$', "vcar", name="kinger_vcar"),
        url(r'^unread_list/$', "unread_list", name="kinger_unread_list"),
        url(r'^daily_record/$', "daily_record", name="kinger_daily_record"),
        url(r'^daily_activity/(?P<active_id>\d+)/$', "daily_activity", name="kinger_daily_activity"),
        url(r'^daily_cookbook/(?P<cid>\d+)/$', "daily_cookbook", name="kinger_daily_cookbook"),
        url(r'^daily_date/$', "get_daily_by_date", name="get_daily_by_date"),
        url(r'^mark_cookbook_as_read/$', "mark_cookbook_as_read", name="kinger_mark_cookbook_as_read"),
        url(r'^introduction/$', "introduction", name="kinger_introduction"),
)

urlpatterns += patterns("kinger.views.revision",
        url(r'^rev/$', "edu_index", name="kinger_edu_index"),
        url(r'^$', "edu_index", name="kinger_edu_index"),
        url('^rev/edu/$', "life_edu", name="kinger_life_edu_index"),
        url('^rev/baby/$', "baby_index", name="kinger_baby_index"),
        url('^rev/cal/$', "cal", name="kinger_rev_cal"),
        url('^rev/axis/$', "time_axis", name="kinger_rev_time_axis"),
        url('^rev/commentshow/(?P<id>\d+)/$', 'show_comment', name='kinger_rev_showcomment'),
        url('^rev/axis_effective_date/$', "axis_effective_date", name="kinger_rev_axis_effective_date"),
        
        
        
#        url('^rev/test/$', "test", name="kinger_test"),
#        url(r'^rev/$', "edu_index", name='home'),
        url('^rev/tile/(?P<tile_id>\d+)/$', "view", name='rev_tile_view'),
        url('^rev/tile/comment/(?P<comment_id>\d+)/delete/$', "delete_comment", name='rev_tile_delete_comment'),
        url(r'^rev/get_user_info/$', "get_user_info", name="kinger_rev_get_user_info"), 
        url(r'^rev/vcar/$', "vcar", name="kinger_rev_vcar"),
        url(r'^rev/unread_list/$', "unread_list", name="kinger_rev_unread_list"),
        url(r'^rev/daily_record/$', "daily_record", name="kinger_rev_daily_record"),
        url(r'^rev/daily_activity/(?P<active_id>\d+)/$', "daily_activity", name="kinger_rev_daily_activity"),
        url(r'^rev/daily_cookbook/(?P<cid>\d+)/$', "daily_cookbook", name="kinger_rev_daily_cookbook"),
        url(r'^rev/daily_date/$', "get_daily_by_date", name="rev_get_daily_by_date"),
        url(r'^rev/mark_cookbook_as_read/$', "mark_cookbook_as_read", name="kinger_rev_mark_cookbook_as_read"),
        url(r'^rev/introduction/$', "introduction", name="kinger_rev_introduction"),
)

urlpatterns += patterns("kinger.views.axis",
        url('^axis/$', "time_axis", name="kinger_time_axis"),
        url('^axis/get_daily_baby_tiles/$', "get_daily_baby_tiles", name="kinger_axis_daily_baby_tiles"),
        url('^axis/(?P<tile_id>\d+)/$', "tile_view", name='axis_tile_view'),
        url('^axis_pre/(?P<tile_id>\d+)/$', "tile_view_pre", name='axis_tile_view_pre'),
        
        url('^axis/tile_page/(?P<tile_id>\d+)/$', "tile_page", name='axis_tile_page'),
        url('^axis/more_comment/(?P<tile_id>\d+)/$', "more_comment", name='axis_more_comment'),
        url(r'^axis/daily_record/$', "daily_record", name="kinger_axis_daily_record"),
        url(r'^axis/daily_activity/$', "daily_activity", name="kinger_axis_daily_activity"),
        url(r'^axis/daily_cookbook/$', "daily_cookbook", name="kinger_axis_daily_cookbook"),
        url('^axis/create_baby_tile/$', "create_baby_tile", name="kinger_rev_create_baby_tile"),
        url('^axis/tile/n_comments/$', "get_tile_n_comments", name="axis_get_tile_n_comments"),
        url('^axis/tile/delete/(?P<tile_id>\d+)/$', "delete_tile", name="axis_delete_tile"),
        url('^axis/tile/description/$', "edit_tile_description", name="axis_edit_tile_description"),
        url('^rev/theme/$', "theme_view", name="kinger_rev_theme_view"),
)

              
# 找回密码各项
urlpatterns += patterns("kinger.views.account",
    url(r'^accounts/pwd_back_mail/$', "pwd_back_mail", name="kinger_pwd_back_mail"),
    url(r'^accounts/pwd_back_mail_done/$', "pwd_back_mail_done", name="kinger_pwd_back_mail_done"),
    url(r'^accounts/pwd_back_mail_reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
     'pwd_back_mail_reset',
   name='kinger_pwd_back_mail_reset'),


    url(r'^accounts/pwd_back_mobile/$', "pwd_back_mobile", name="kinger_pwd_back_mobile"),
    url(r'^accounts/pwd_back_mobile_get_vcode/$', "pwd_back_mobile_get_vcode", name="kinger_pwd_back_mobile_get_vcode"),

    url(r'^accounts/pwd_back_pwd_reset/$', "pwd_back_pwd_reset", name="kinger_pwd_back_pwd_reset"),
    url(r'^accounts/pwd_back_success/$', "pwd_back_success", name="kinger_pwd_back_success"),        
)

urlpatterns += patterns("kinger.views.cross_domain",
    url(r'^cross_domain/login/$', "cross_domain_login", name='cross_domain_login'),
    url(r'^cross_domain/logout/$', "cross_domain_logout", name='cross_domain_logout'),
)

urlpatterns += patterns("kinger.views.admin.advimage",
        url(r'^upload_image/$', "upload_image", name="upload_image"),
        url(r'^upload_tile_image/$', "upload_tile_image", name="upload_tile_image"),
)

urlpatterns += patterns("kinger.views.statistical.weixiao",
        url(r'^statistical/$', "index", name="statistical_index"),                
        url(r'^statistical/group_teacher/$', "group_teacher", name="statistical_group_teacher"),
        url(r'^statistical/school_group/$', "school_group", name="statistical_school_group"),
        url(r'^statistical/school_student/$', "school_student", name="statistical_school_student"),
        url(r'^statistical/tile_visit/$', "student_tile_visit", name="statistical_tile_visit"),
        url(r'^statistical/page_request_time/$', "page_request_time", name="statistical_page_request_time"),
)

urlpatterns += patterns("kinger.views.ykauth",
        url(r'^YKAuth.txt/$', "index", name="ykauth"),
)

urlpatterns += patterns('',
                        
    url(r'^admin/', include('kinger.views.admin.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^grappelli/', include('grappelli.urls')),
    # # Edit profile
    url(r'^accounts/(?P<username>[\.\w]+)/edit/$',
       "userena.views.profile_edit", {'edit_profile_form': KEditProfileForm},
       name='userena_profile_edit'),
    url(r'^account_setting/$', 'userena.views.account_setting', name="userena_account_setting"),
    url(r'^accounts/signup/$',
       "userena.views.signup", {'signup_form': KSignupForm},
       name='userena_signup'),
    # Change email and confirm it
    url(r'^accounts/(?P<username>[\.\w]+)/email/$',
       "userena.views.email_change", {"email_form": KChangeEmailForm},
       name='userena_email_change'),
    url(r'^accounts/signin/$',
       "userena.views.signin", {"auth_form": KAuthenticationForm},
       name='userena_signin'),
    (r'^accounts/', include('userena.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^manage/', include('manage.urls')),

    # 专家问答
    (r'^aq/', include('aq.urls')),

    # 客服问答
    (r'^waiter/', include('waiter.urls')),

    # 短信相关
    (r'^sms/', include('sms.urls')),
    
    #oa
    (r'^oa/', include('oa.urls')),
    (r'^supply/', include('oa.supply.urls')),
#    (r'^oa/site/', include('oa.views.site.urls')),

    (r'^growth/', include('kinger.growth.urls')),
    # 站内提醒
    ('^notification/', include('notifications.urls',namespace='notifications')),

    (r'^photologue/', include('photologue.urls')),
    url(r'^like/', include('likeable.urls')),


    #(r'^messages/', include('userena.contrib.umessages.urls')),

    #url(r'^message/(?P<message_id>\d+)/delete/$',        "kinger.views.message.message_delete",        name='userena_umessages_delete'),

    (r'^client/', include('kinger.apps.client.urls')),
    (r'^oauth2/', include('kinger.apps.oauth2.urls')),
    (r'^api/v1/', include('api.urls',app_name='api')),
    (r'^api/v2/', include('apiv2.urls',app_name='apiv2')),

    (r'^backend/', include('backend.urls')),

    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/_static/img/favicon.ico'}),

)

urlpatterns += patterns("kinger.views.message",
    url(r'^messages/$',
        "message_list",
        name='userena_umessages_list'),
    
    url(r'^message/history/(?P<uid>\d+)/$',
        "user_message_history",
        name='user_umessages_history'),
    
    url(r'^message/history/(?P<username>[\.\w]+)/$',
        "message_history",
        name='userena_umessages_history'),
                        
    url(r'^message/quick_contact/$',
        "message_quick_contact",
        name='userena_umessages_quick_contact'),

    url(r'^message/remove/$',
        "message_remove",
        name='userena_umessages_remove'),

    url(r'^message/contact_remove/(?P<username>[\.\w]+)$',
        "contact_remove",
        name='userena_umessages_contact_remove'),
)

urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),
)

urlpatterns += patterns('kinger.views.test',
    url(r'^tests/', 'test'),
)

urlpatterns += patterns('',
    url(r'^site_file/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.FILE_PATH}),
)

urlpatterns += patterns('',
    # media 目录
    url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
        'django.views.static.serve', {"document_root": settings.MEDIA_ROOT}),
)

urlpatterns += patterns('',
    # media 目录
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:],
        'django.views.static.serve', {"document_root": settings.STATIC_ROOT}),
)

urlpatterns += patterns('',
    url(r'^oa/site/', include('oa.views.site.urls')),
    url(r'^(?P<domain>[\.\w]+)/', include('oa.views.site.urls')),
)

if settings.DEBUG is False:
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )
