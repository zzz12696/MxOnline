import json

from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q

from .models import CourseOrg, CityDict, Teacher
from .forms import UserAskForm
from operation.models import UserFavorite
from courses.models import Course


class OrgView(View):
    '''
    课程机构列表功能
    '''
    def get(self, request):
        # 课程机构
        all_orgs = CourseOrg.objects.all()
        hot_orgs = all_orgs.order_by('-click_nums')[:3]

        # 机构搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(
                Q(name__icontains=search_keywords)
                |Q(desc__icontains=search_keywords)
            )

        # 城市
        all_cities = CityDict.objects.all()

        # 城市筛选
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 类别筛选
        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)

        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by('-student_nums')
            elif sort == 'courses':
                all_orgs = all_orgs.order_by('-course_nums')

        # 机构数目总数
        org_nums = all_orgs.count()

        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_orgs, 2, request=request)

        orgs = p.page(page)

        return render(request, 'organization/org-list.html', {
            'all_orgs': orgs,
            'all_cities': all_cities,
            'org_nums': org_nums,
            'city_id': city_id,
            'category': category,
            'hot_orgs': hot_orgs,
            'sort': sort,
        })


class AddUserAskView(View):
    '''
    用户添加咨询
    '''
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            name_dict = {'status': 'success'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')
        else:
            name_dict = {'status': 'fail', 'msg': '添加出错'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')


class OrgHomeView(View):
    '''
    机构首页
    '''
    def get(self, request, org_id):
        current_page = 'home'
        course_org = CourseOrg.objects.get(id=int(org_id))

        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        all_courses = course_org.course_set.all()  # django ORM反向取值
        all_teachers = course_org.teacher_set.all()
        return render(request, 'organization/org-detail-homepage.html', {
            'all_courses': all_courses,
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgCourseView(View):
    '''
    机构课程列表页
    '''
    def get(self, request, org_id):
        current_page = 'course'
        course_org = CourseOrg.objects.get(id=int(org_id))

        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        all_courses = course_org.course_set.all()  # django ORM反向取值
        return render(request, 'organization/org-detail-course.html', {
            'all_courses': all_courses,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgDescView(View):
    '''
    机构介绍页
    '''
    def get(self, request, org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))

        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'organization/org-detail-desc.html', {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgTeacherView(View):
    '''
    机构讲师页
    '''
    def get(self, request, org_id):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))

        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        all_teachers = course_org.teacher_set.all()
        return render(request, 'organization/org-detail-teachers.html', {
            'course_org': course_org,
            'all_teachers': all_teachers,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class AddFavView(View):
    '''
    用户收藏，用户取消收藏
    '''
    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)

        # 判断用户登录状态
        if not request.user.is_authenticated():
            name_dict = {'status': 'fail', 'msg': '用户未登录'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')

        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        # 如果记录已经存在，则表示用户取消收藏
        if exist_records:
            exist_records.delete()
            name_dict = {'status': 'success', 'msg': '收藏'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()

                name_dict = {'status': 'success', 'msg': '已收藏'}
                return HttpResponse(json.dumps(name_dict), content_type='application/json')
            else:
                name_dict = {'status': 'fail', 'msg': '收藏出错'}
                return HttpResponse(json.dumps(name_dict), content_type='application/json')


class TeacherListView(View):
    '''
    课程讲师列表页
    '''
    def get(self, request):

        all_teachers = Teacher.objects.all()

        # 授课讲师搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teachers = all_teachers.filter(
                Q(name__icontains=search_keywords)
                |Q(work_company__icontains=search_keywords)
                |Q(work_position__icontains=search_keywords)
            )

        # 条件排序功能
        sort = request.GET.get('sort', '')
        if sort == 'hot':
            all_teachers = all_teachers.order_by('-click_nums')

        # 排行榜讲师
        sorted_teachers = Teacher.objects.all().order_by('-click_nums')[:3]

        # 讲师总数
        teacher_nums = all_teachers.count()

        # 对讲师进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_teachers, 2, request=request)

        teachers = p.page(page)

        return render(request, 'teacher/teachers-list.html', {
            'all_teachers': teachers,
            'teacher_nums': teacher_nums,
            'sort': sort,
            'sorted_teachers': sorted_teachers,
        })


class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        all_courses = Course.objects.filter(teacher=teacher)

        # 排行榜讲师
        sorted_teachers = Teacher.objects.all().order_by('-click_nums')[:3]

        has_teacher_fav = False
        has_org_fav = False
        if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
            has_teacher_fav = True
        if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org_id):
            has_org_fav = True

        return render(request, 'teacher/teacher-detail.html', {
            'teacher': teacher,
            'all_courses': all_courses,
            'sorted_teachers': sorted_teachers,
            'has_teacher_fav': has_teacher_fav,
            'has_org_fav': has_org_fav,
        })