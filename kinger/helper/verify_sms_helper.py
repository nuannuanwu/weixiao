# -*- coding: utf-8 -*-
from kinger.models import VerifySms, Sms
from kinger.profiles.models import Profile
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
import random
import datetime

def generate_vcode():
	vcode = ''
	for i in range(0,6):
		vcode += random.choice('0123456789')

	return vcode

def generate_vcode_for_user(user):
	"""
	为某个用户生出验证码记录到verifySms中，并发送
	"""
	vcode = generate_vcode()

	current_site = Site.objects.get_current()
	site_name = current_site.name
	
	mobile = user.get_profile().mobile

	#保存，发送短信
	sms_content = "尊敬的用户，您的验证码是:"+ vcode +"，请在页面中填写验证码完成密码重置，" +"【" + site_name.encode("utf-8") + "】"
	print sms_content

	VerifySms.objects.set_vcode_invalid(user)

	sender = User.objects.filter(is_superuser=1).latest('pk')
	sms = Sms.objects.create_verify_sms(sender=sender, mobile=mobile, receiver=user, content=sms_content)
	vsms = VerifySms(sms=sms,user=user,mobile=mobile,content=sms_content,vcode=vcode)
	vsms.save()

	return vcode

def get_user_from_mobile(mobile):
	"""
	根据手机号码得到用户。多个用户默认为第一个用户
	"""
	profiles = Profile.objects.filter(mobile=mobile)  
	pro_num = profiles.count()

	if pro_num > 0: 
		return profiles[0].user

def get_vcode(mobile):
	"""
	根据用户的号码，产生验证码短信。验证码有效期为30分钟，1分钟产生一次。
	"""

	CODES = dict(NOT_FOUND = ('该手机号码尚未绑定微校账号', 0,{}),
	             ONE_FORBIDDEN = ('一分钟内，无法再次生成验证码', 1,{'time':None}),
	             ONE_MORE = ('新的验证码已发送到您的手机，请查看。', 2,{}),
	             NEW = ('验证码已发送到您的手机，请查看。', 200,{}))
	seconds_num = 60

	user = get_user_from_mobile(mobile)

	if user:
		verify_sms = VerifySms.objects.get_valid_vsms(user)

		if verify_sms:
			time = verify_sms.ctime
			now = datetime.datetime.now()
			seconds = (now - time).seconds			

			if seconds >= seconds_num:
				generate_vcode_for_user(user)
				return CODES['ONE_MORE']
			else:
				CODES['ONE_FORBIDDEN'][2]['time'] = seconds_num - seconds
				return CODES['ONE_FORBIDDEN']
		else:
			generate_vcode_for_user(user)
			return CODES['NEW']
	else:
		return CODES['NOT_FOUND']






