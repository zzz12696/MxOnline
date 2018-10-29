from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(required=True, error_messages={'required': '用户名不能为空'})  # 必填字段
    password = forms.CharField(required=True, min_length=6, error_messages={
        'required': '密码不能为空',
        'min_length': '密码不能小于6位',
    })