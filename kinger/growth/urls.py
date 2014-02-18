# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url


urlpatterns = patterns("kinger.growth.views.books",
    url(r'^oa/$', "oa_index", name='growth_oa_index'),
    url(r'^index/$', "growth_index", name="growth_index"),
    url(r'^source_list/(?P<group_id>\d+)/$', "source_list", name="growth_source_list"),
)

urlpatterns += patterns("kinger.growth.views.phantomjs",
    url(r'^phantomjs/test/$', "test", name="growth_phantomjs_test"),
)



