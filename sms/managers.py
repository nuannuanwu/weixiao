# -*- coding: utf-8 -*-

from django.db import models

class SmsSendAccountManager(models.Manager):

    def get_one_port(self, exclude_list=[]):
        """
        随机得到一个有效的端口号
        """
        return self.exclude(status__startswith='-',uc__in=exclude_list).filter(user_id=1).order_by('?')[0].uc

    def is_valid_port(self, port):
    	"""
    	验证端口的有效性
    	"""
    	return port[0] != '-'