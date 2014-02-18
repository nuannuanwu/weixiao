# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url


urlpatterns = patterns("oa.supply.views.supplies",
    url(r'^category/$', "supply_category", name='oa_supply_category'),
    url(r'^index/$', "supply_index", name='oa_supply_index'),
    url(r'^providers/$', "provider_index", name='oa_provider_index'),
    url(r'^provider/add/$', "create_provider", name='oa_provider_create'),
    url(r'^school/providers/$', "get_school_provider", name='oa_school_providers'),
    url(r'^provider/update/(?P<provider_id>\d+)/$', "update_provider", name='oa_provider_update'),
    url(r'^update/(?P<supply_id>\d+)/$', "update_supply", name='oa_supply_update'),
    url(r'^records/$', "record_list", name='oa_supply_record_index'),
    url(r'^record/detail/(?P<record_id>\d+)/$', "record_detail",name='oa_supply_record_detail'),
    url(r'^category/extra/$', "get_extra_form", name='oa_supply_category_extra'),
    url(r'^school_realtes/$', "school_realtes", name='oa_supply_school_realtes'),
    url(r'^record/delete/(?P<record_id>\d+)/$', "delete_record",name='oa_supply_record_delete'),
    url(r'^record/reback/(?P<record_id>\d+)/$', "reback_record",name='oa_supply_record_reback'),
    url(r'^record_supply/reback/(?P<record_id>\d+)/$', "reback_supply",name='oa_supply_reback_supply'),
    url(r'^supply/entry/$', "supply_entry", name='oa_supply_supply_entry'),
    url(r'^supply/back/$', "supply_back", name='oa_supply_supply_back'),
    url(r'^supply/delete_category/(?P<cat_id>\d+)/$', "delete_category",name='oa_supply_delete_category'),  
)

urlpatterns += patterns("oa.supply.views.document",
    url(r'^document/receive/$', "my_document", name='oa_supply_my_document'),
    url(r'^document/write/$', "write_document", name='oa_supply_write_document'),
    url(r'^document/issued_document/$', "issued_document",name='oa_supply_issued_document'),
    url(r'^document/detail/(?P<doc_id>\d+)/$', "document_detail",name='oa_supply_document_detail'),
    url(r'^document/need_approval/$', "need_approval",name='oa_supply_document_need_approval'),
    url(r'^document/approval_document/(?P<doca_id>\d+)/$', "approval_document",name='oa_supply_approval_document'),
    url(r'^document/having_approvaled/$', "having_approvaled",name='oa_supply_having_approvaled'),
    url(r'^document/reback_document/$', "reback_document",name='oa_supply_reback_document'),
    url(r'^document/edit_reback_document/(?P<doca_id>\d+)/$', "edit_reback_document",name='oa_supply_edit_reback_document'),
    url(r'^document/invalid_user_document/(?P<doc_id>\d+)/$', "invalid_user_document",name='oa_supply_invalid_user_document'),
    url(r'^document/invalid_document/$', "invalid_document",name='oa_supply_invalid_document'),
    url(r'^document/personal_document/$', "personal_document",name='oa_supply_personal_document'),
    url(r'^document/delete_document/(?P<doc_id>\d+)/$', "delete_document",name='oa_supply_delete_document'),
    url(r'^document/update/(?P<doc_id>\d+)/$', "update_document",name='oa_supply_update_document'),
    url(r'^document/cancel/(?P<doc_id>\d+)/$', "cancel_document",name='oa_supply_cancel_document'),
    url(r'^document/download/(?P<file_id>\d+)/$', "download_document",name='oa_supply_download_document'),
    url(r'^document/delete_file/$', "delete_document_file",name='oa_supply_delete_document_file'),
    url(r'^document/download_zip/(?P<doc_id>\d+)/$', "download_zipfile",name='oa_supply_download_zip_document'),
    url(r'^document/document_applies/$', "document_applies",name='oa_supply_document_applies'),
    url(r'^document/resave/(?P<doc_id>\d+)/$', "resave_document",name='oa_supply_resave_document'),
)


urlpatterns += patterns("oa.supply.views.disk",
    url(r'^disk/index/$', "disk_index", name='oa_disk_index'),
    url(r'^disk/category/$', "disk_category", name='oa_disk_category'),
    url(r'^disk/create/$', "create_disk", name='oa_disk_create'),
    url(r'^disk/detail/(?P<disk_id>\d+)/$', "disk_detail",name='oa_sdisk_detail'),
    url(r'^disk/update/(?P<disk_id>\d+)/$', "update_disk",name='oa_sdisk_update'),
    url(r'^disk/get_extra_form/$', "get_extra_form",name='oa_disk_get_extra_form'),
    url(r'^disk/delete_category/(?P<cat_id>\d+)/$', "delete_category",name='oa_disk_delete_category'),  
)


