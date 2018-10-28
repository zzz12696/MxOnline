from datetime import datetime

from django.db import models


class CityDict(models.Model):
    name = models.CharField(verbose_name='城市名', max_length=20)
    desc = models.CharField(verbose_name='描述', max_length=200)
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.now)

    class Meta:
        verbose_name = '城市'
        verbose_name_plural= verbose_name


class CourseOrg(models.Model):
    name = models.CharField(verbose_name='机构名称', max_length=50)
    desc = models.TextField(verbose_name='机构描述')
    click_nums = models.IntegerField(verbose_name='点击数', default=0)
    fav_nums = models.IntegerField(verbose_name='收藏数', default=0)
    image = models.ImageField(verbose_name='封面图', upload_to='org/image/%Y/%m', max_length=100)
    address = models.CharField(verbose_name='机构地址', max_length=50)
    city = models.ForeignKey(CityDict, verbose_name='所在城市')
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.now)

    class Meta:
        verbose_name = '课程机构'
        verbose_name_plural = verbose_name


class Teacher(models.Model):
    name = models.CharField(verbose_name='教师名', max_length=50)
    org = models.ForeignKey(CourseOrg, verbose_name='所属机构')
    work_years = models.IntegerField(verbose_name='工作年限', default=0)
    work_company = models.CharField(verbose_name='就职公司', max_length=50)
    work_position = models.CharField(verbose_name='公司职位', max_length=50)
    points = models.CharField(verbose_name='教学特点', max_length=50)
    click_nums = models.IntegerField(verbose_name='点击数', default=0)
    fav_nums = models.IntegerField(verbose_name='收藏数', default=0)
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.now)

    class Meta:
        verbose_name = '教师'
        verbose_name_plural = verbose_name