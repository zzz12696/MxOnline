import json

from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password  # django自带的密码加密函数
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import UserProfile, EmailVerifyRecord, Banner
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from courses.models import Course


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class IndexView(View):
    '''
    慕学在线网首页
    '''
    def get(self, request):
        # 取出轮播图
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=False)[:3]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs,
        })


class LoginView(View):
    '''
    用户登录
    '''
    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get('username', '')
            pass_word = request.POST.get('password', '')
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, 'login.html', {'msg': '用户未激活'})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误'})
        else:
            return render(request, 'login.html', {'login_form': login_form})


class LogoutView(View):
    '''
    用户退出
    '''
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


# TODO: 注册成功前台不会收到任何反馈信息，用户体验不好
class RegisterView(View):
    '''
    用户注册
    '''
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email', '')
            if UserProfile.objects.filter(username=user_name):
                return render(request, 'register.html', {'register_form': register_form, 'msg': '用户已存在'})
            pass_word = request.POST.get('password', '')
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)
            user_profile.save()

            # 写入欢迎注册消息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = '欢迎注册慕学在线网'
            user_message.save()


            send_register_email(user_name, 'register')
            return render(request, 'send_success.html')
        else:
            return render(request, 'register.html', {'register_form': register_form})


# TODO: 激活登录之后，URL还是停留在login
class ActiveUserView(View):
    '''
    用户激活账号
    '''
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, 'active_fail.html')
        return render(request, 'login.html')


class ForgetPwdView(View):
    '''
    用户忘记密码
    '''
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, 'forgetpwd.html', {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            send_register_email(email, 'forget')
            return render(request, 'send_success.html')
        else:
            return render(request, 'forgetpwd.html', {'forget_form': forget_form, 'msg': ''})


# TODO: 激活登录之后，URL还是停留在login
class ResetView(View):
    '''
    用户重置密码
    '''
    def get(self, request, reset_code):
        all_records = EmailVerifyRecord.objects.filter(code=reset_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, 'password_reset.html', {'email': email})
        else:
            return render(request, 'active_fail.html')
        return render(request, 'login.html')


# TODO: 修改密码链接重复性验证
class ModifyPwdView(View):
    '''
    修改用户密码
    '''
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            if pwd1 != pwd2:
                return render(request, 'password_reset.html', {'email': email, 'msg': '密码不一致'})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd1)
            user.save()
            return render(request, 'login.html')
        else:
            email = request.POST.get('email', '')
            return render(request, 'password_reset.html', {'email': email, 'modify_form': modify_form})


class UserInfoView(LoginRequiredMixin, View):
    '''
    用户个人信息
    '''
    def get(self, request):
        return render(request, 'usercenter/usercenter-info.html', {})

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            name_dict = {'status': 'success'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class UploadImageView(LoginRequiredMixin, View):
    '''
    用户修改头像
    '''
    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            name_dict = {'status': 'success'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')
        else:
            name_dict = {'status': 'fail'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')


class UpdatePwdView(View):
    '''
    个人中心修改用户密码
    '''
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                name_dict = {'status': 'fail', 'msg': '密码不一致'}
                return HttpResponse(json.dumps(name_dict), content_type='application/json')
            user = request.user
            user.password = make_password(pwd1)
            user.save()
            name_dict = {'status': 'success'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin, View):
    '''
    发送邮箱验证码
    '''
    def get(self, request):
        email = request.GET.get('email', '')

        if UserProfile.objects.filter(email=email):
            name_dict = {'email': '邮箱已经存在'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')
        send_register_email(email, 'update_email')
        name_dict = {'status': 'success'}
        return HttpResponse(json.dumps(name_dict), content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    '''
    修改个人邮箱
    '''
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            name_dict = {'email': '邮箱修改成功'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')
        else:
            name_dict = {'email': '验证码出错'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    '''
    我的课程
    '''
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter/usercenter-mycourse.html', {
            'user_courses': user_courses,
        })


class MyFavOrgView(LoginRequiredMixin, View):
    '''
    我收藏的课程机构
    '''
    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, 'usercenter/usercenter-fav-org.html', {
            'org_list': org_list,
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    '''
    我收藏的课程机构
    '''
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter/usercenter-fav-teacher.html', {
            'teacher_list': teacher_list,
        })


class MyFavCourseView(LoginRequiredMixin, View):
    '''
    我收藏的公开课
    '''
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'usercenter/usercenter-fav-course.html', {
            'course_list': course_list,
        })


class MyMessageView(LoginRequiredMixin, View):
    '''
    我的消息
    '''
    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)

        # 用户进入个人消息之后清空所有未读消息
        all_unread_messages = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()

        # 对个人消息进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_messages, 2, request=request)

        messages = p.page(page)

        return render(request, 'usercenter/usercenter-message.html', {
            'all_messages': messages,
        })


def page_not_found(request):
    '''
    全局404处理函数
    :param request:
    :return:
    '''
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    '''
    全局500处理函数
    :param request:
    :return:
    '''
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response