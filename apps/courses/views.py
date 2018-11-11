import json

from django.shortcuts import render, HttpResponse
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import Course, CourseResource, Video
from operation.models import UserFavorite, CourseComments, UserCourse
from utils.mixin_utils import LoginRequiredMixin


class CourseListView(View):
    '''
    课程列表页
    '''
    def get(self, request):
        all_courses = Course.objects.all().order_by('-add_time')

        hot_courses = Course.objects.all().order_by('-click_nums')[:3]

        # 课程排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_courses = all_courses.order_by('-students')
            elif sort == 'hot':
                all_courses = all_courses.order_by('-click_nums')

        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, 3, request=request)

        courses = p.page(page)

        return render(request, 'courses/course-list.html', {
            'all_courses': courses,
            'sort': sort,
            'hot_courses': hot_courses,
        })


class CourseDetailView(View):
    '''
    课程详情页
    '''
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        # 增加课程点击数
        course.click_nums += 1
        course.save()

        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        # 相关课程推荐
        tag = course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:1]
        else:
            relate_courses = []

        return render(request, 'courses/course-detail.html', {
            'course': course,
            'relate_courses': relate_courses,
            'has_fav_course': has_fav_course,
            'has_fav_org': has_fav_org,
        })


class CourseInfoView(LoginRequiredMixin, View):
    '''
    课程章节信息
    LoginRequiredMixin 用于实现开始学习的登录认证
    '''
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.students += 1
        course.save()

        # 查询该用户是否已经关联了该课程
        user_course = UserCourse.objects.filter(user=request.user, course=course)
        if not user_course:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 根据当前课程取出学习该课程的所有用户id
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        # 根据用户id取出他们学习的所有课程，作为相关课程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有相关课程id，但不包含本课程
        course_ids = [user_course.course.id for user_course in all_user_courses if user_course.course.id != course.id]
        # 获取学过该课程的用户的其他所有课程，只取点击数排前五个
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'courses/course-video.html', {
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
        })


class CourseCommentView(LoginRequiredMixin, View):
    '''
    课程评论
    '''
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course).order_by('-add_time')
        return render(request, 'courses/course-comment.html', {
            'course': course,
            'all_resources': all_resources,
            'all_comments': all_comments,
        })


class AddCommentsView(View):
    '''
    用户添加课程评论
    '''
    def post(self, request):
        if not request.user.is_authenticated():
            # 判断用户登录状态
            name_dict = {'status': 'fail', 'msg': '用户未登录'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')

        course_id = request.POST.get('course_id', 0)
        comments = request.POST.get('comments', '')
        if int(course_id) > 0 and comments:
            course_comments = CourseComments()
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()

            name_dict = {'status': 'success', 'msg': '添加成功'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')
        else:
            name_dict = {'status': 'fail', 'msg': '添加失败'}
            return HttpResponse(json.dumps(name_dict), content_type='application/json')


class VideoPlayView(View):
    '''
    视频播放页面
    '''
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))

        course = video.lesson.course
        course.students += 1
        course.save()

        # 查询该用户是否已经关联了该课程
        user_course = UserCourse.objects.filter(user=request.user, course=course)
        if not user_course:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 根据当前课程取出学习该课程的所有用户id
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        # 根据用户id取出他们学习的所有课程，作为相关课程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有相关课程id，但不包含本课程
        course_ids = [user_course.course.id for user_course in all_user_courses if user_course.course.id != course.id]
        # 获取学过该课程的用户的其他所有课程，只取点击数排前五个
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'courses/course-play.html', {
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
            'video': video,
        })