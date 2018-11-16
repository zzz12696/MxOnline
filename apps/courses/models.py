from datetime import datetime

from django.db import models

from organization.models import CourseOrg, Teacher


class Course(models.Model):
    name = models.CharField(verbose_name='课程名', max_length=50)
    course_org = models.ForeignKey(CourseOrg, verbose_name='课程所属机构', null=True)
    desc = models.CharField(verbose_name='课程描述', max_length=300)
    teacher = models.ForeignKey(Teacher, verbose_name='讲师', null=True, blank=True)
    detail = models.TextField(verbose_name='课程详情')
    is_banner = models.BooleanField(verbose_name='是否轮播图', default=False)
    degree = models.CharField(verbose_name='课程难度', max_length=2, choices=(('cj', '初级'), ('zj', '中级'), ('gj', '高级')))
    learn_times = models.IntegerField(verbose_name='学习时长(分钟数)', default=0)
    category = models.CharField(verbose_name='课程类别', max_length=20, default='程序开发')
    tag = models.CharField(verbose_name='课程标签', default='', max_length=10)
    you_need_know = models.CharField(verbose_name='课程须知', max_length=300, null=True, blank=True)
    teacher_tell = models.CharField(verbose_name='老师告诉你', max_length=300, null=True, blank=True)
    students = models.IntegerField(verbose_name='学习人数', default=0)
    fav_nums = models.IntegerField(verbose_name='收藏人数', default=0)
    image = models.ImageField(verbose_name='封面图', upload_to='courses/image/%Y/%m', max_length=100, blank=True, null=True)
    click_nums = models.IntegerField(verbose_name='点击量', default=0)
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.now)

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_zj_nums(self):
        '''
        获取课程章节数
        :return:
        '''
        all_lessons = self.lesson_set.all().count()
        return all_lessons

    def get_learn_users(self):
        '''
        获取学习该课程的用户
        :return:
        '''
        return self.usercourse_set.all()[:5]

    def get_course_lesson(self):
        '''
        获取课程所有章节
        :return:
        '''
        return self.lesson_set.all()


class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name='课程')
    name = models.CharField(verbose_name='章节名', max_length=100)
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.now)

    class Meta:
        verbose_name = '章节'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_lesson_video(self):
        '''
        获取章节视频
        :return:
        '''
        return self.video_set.all()


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name='章节')
    name = models.CharField(verbose_name='视频名', max_length=100)
    url = models.CharField(verbose_name='访问地址', max_length=200, default='')
    learn_times = models.IntegerField(verbose_name='学习时长(分钟数)', default=0)
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.now)

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name='课程')
    name = models.CharField(verbose_name='名称', max_length=100)
    download = models.FileField(verbose_name='资源文件', upload_to='course/resource/%Y/%m', max_length=100)
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.now)

    class Meta:
        verbose_name = '课程资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name