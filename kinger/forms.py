# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from kinger.validators import kinger_validate_email
from django import forms
from userena.forms import SignupForm, ChangeEmailForm, EditProfileForm, AuthenticationForm
from kinger import helpers
from django.contrib.auth import authenticate
from kinger.models import Tile, VerifySms
from django.forms import ModelForm
from captcha.fields import CaptchaField
from kinger.validators import validate_mobile_number
from django.core.validators import RegexValidator
from kinger.helper import verify_sms_helper
from bootstrap.forms import BootstrapForm, Fieldset, BootstrapMixin

attrs_dict = {'class': 'required'}


class KSignupForm(SignupForm):
    """
    覆盖 ``userena.SignupForm``. 通过给 ``userena`` 的 view 投递``form`` 即可，操作如下::

        url(r'^accounts/signin/$',
            "userena.views.signin", {"auth_form": KAuthenticationForm},
            name='userena_signin'),

    """

    # 限定了用户名只支持英文字母和下划线.其原来支持 `.` `..` 等特殊字符.
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("Username"),
                                error_messages={'invalid': _('Username must contain only letters, numbers and underscores.')})

    # 增加了自定义的校验规则，不允许中文域名
    email = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("Email"),
                             validators=[kinger_validate_email])


class KChangeEmailForm(ChangeEmailForm):
    email = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("Email"),
                             validators=[kinger_validate_email])


class KEditProfileForm(EditProfileForm):
    """
    | 覆盖 ``userena EditProfileForm``.
    | 定义头像字段html渲染样式
    """
    def __init__(self, *args, **kwargs):
        super(KEditProfileForm, self).__init__(*args, **kwargs)
        self.fields['mugshot'].widget.template_with_initial = u'%(input)s'

    def clean_birth_date(self):
        """
        限定出生日期的范围: ``1800 ~ today ``
        """
        birth_date = self.cleaned_data['birth_date']
        return helpers.clean_birthday_rang(birth_date)


class KAuthenticationForm(AuthenticationForm):
    def clean(self):
        """
        Checks for the identification and password.

        If the combination can't be found will raise an invalid sign in error.

        ``userena`` 对用户名和 email 都是忽略大小写的，但原错误却提示不忽略大小写. 所以修改错误提示信息
        """
        identification = self.cleaned_data.get('identification')
        password = self.cleaned_data.get('password')

        if identification and password:
            user = authenticate(identification=identification, password=password)
            if user is None:
                raise forms.ValidationError(_(u"Please enter a correct username or email and password. Note that both fields are case-insensitive."))
        return self.cleaned_data

from django.db import models
from kinger.models import NewTileType
class TileCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """


 
    LOOKUP_CHOICES = (
        #(u'0', u'教师发布'),
        (1, u'育儿频道'),
        (2, u'生命学堂'),
        )

    TYPE_CHOICES = (
        ('', '------'),
        (1, u'图片'),
        (2, u'视频'),
        )

    is_tips = forms.ChoiceField(initial="1",choices=LOOKUP_CHOICES)
    #type = forms.ChoiceField(choices=TYPE_CHOICES)
    type = models.ForeignKey(NewTileType,verbose_name = _('tile type'),limit_choices_to={'id__in': [1,2]})

class MobileForm(forms.Form):
    """
    用于找回密码的表单，有验证码
    """

    mobile = forms.CharField(max_length=20,validators=[validate_mobile_number])
    captcha = CaptchaField()

class PwdMobileForm(forms.Form):
    mobile = forms.CharField(max_length=20,validators=[validate_mobile_number])
    vcode = forms.CharField(max_length=20,validators=[RegexValidator(r'^[0-9]{6}$', u"输入一个有效的验证码", 'invalid')])

    def clean(self):
        """
        确保找到了用户，并且验证码一致
        """       

        cleaned_data = super(PwdMobileForm, self).clean()
        mobile = cleaned_data.get('mobile')
        vcode = cleaned_data.get('vcode')
        if mobile and vcode:
            user = verify_sms_helper.get_user_from_mobile(mobile)

            if user:
                server_vcode = VerifySms.objects.get_vcode(user=user)

                # 还没有生成验证码
                if not server_vcode:                                   
                    self._errors['mobile'] = self.error_class([u'尊敬的用户，请先生成验证码'])
                    del cleaned_data['mobile']          

                else:               

                    # 有验证码，比对
                    if vcode != server_vcode:
                        self._errors['vcode'] = self.error_class(['您输入的验证码不匹配，请重新录入'])
                        del cleaned_data['vcode']           
            else:
                self._errors['mobile'] = self.error_class(['这个手机号码没有关联任何用户，请检查您的手机号码是否录入正确。'])
                del cleaned_data['mobile']         
            

        return cleaned_data



class PwdResetForm(forms.Form):
    """
    密码重置
    """
    
    pwd = forms.CharField(max_length=16, min_length=6, widget=forms.PasswordInput())
    pwd_b = forms.CharField(max_length=16, min_length=6, widget=forms.PasswordInput())

    def clean(self):
        """
        验证两次密码必须一致
        """
        cleaned_data = super(PwdResetForm, self).clean()
        pwd = cleaned_data.get('pwd')
        pwd_b = cleaned_data.get('pwd_b')
        if pwd and pwd_b:
            if pwd != pwd_b:
                msg = u"两个密码不一致"

                self._errors['pwd'] = self.error_class([msg])
                self._errors['pwd_b'] = self.error_class([msg])

                del cleaned_data['pwd']
                del cleaned_data['pwd_b']

        return cleaned_data


class TileBabyForm(BootstrapMixin, ModelForm):
    class Meta:
        model = Tile
        fields = ("description", "img", "new_type" ,"content")

        layout = (
            Fieldset("",
                "description", "img", "new_type" ,"content"),
            )

    def __init__(self, *args, **kwargs):
        super(TileBabyForm, self).__init__(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        rs = super(TileBabyForm, self).save(*args, **kwargs)
        return rs
