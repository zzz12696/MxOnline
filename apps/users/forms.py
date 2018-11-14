from django import forms
from captcha.fields import CaptchaField

from .models import UserProfile


class LoginForm(forms.Form):
    username = forms.CharField(required=True, error_messages={'required': '用户名不能为空'})  # 必填字段
    password = forms.CharField(required=True, min_length=6, error_messages={
        'required': '密码不能为空',
        'min_length': '密码不能小于6位',
    })


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True, error_messages={'required': '用户名不能为空'})
    password = forms.CharField(required=True, min_length=6, error_messages={
        'required': '密码不能为空',
        'min_length': '密码不能小于6位',
    })
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class ForgetForm(forms.Form):
    email = forms.EmailField(required=True, error_messages={'required': '用户名不能为空'})
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=6)
    password2 = forms.CharField(required=True, min_length=6)


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nick_name', 'gender', 'birthday', 'address', 'mobile']