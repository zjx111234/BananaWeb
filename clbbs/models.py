# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime


# Create your models here.


class Article(models.Model):
    title = models.CharField(u"标题", max_length=255)
    brief = models.CharField(u"文章简介", null=True, blank=True, max_length=150)
    category = models.ForeignKey("Category")
    content = models.TextField(u"文章内容")
    author = models.ForeignKey("UserProfile")
    pub_date = models.DateTimeField(blank=True, null=True)
    last_modify = models.DateTimeField(auto_now=True)
    priority = models.IntegerField(u"优先级", default=1000)
    head_img = models.ImageField(u"图片", upload_to="statics/uploads")
    thumb_count = models.IntegerField(u"点赞数量", default=0)
    status_choices = (('draft', u"草稿"),
                      ('published', u"已发布"),
                      ('hidden', u"隐藏"),
                      )
    status = models.CharField(choices=status_choices, default='published', max_length=32)

    def __str__(self):
        return self.title

    def clean(self):
        # Don't allow draft entries to have a pub_date.
        if self.status == 'draft' and self.pub_date is not None:
            raise ValidationError(('Draft entries may not have a publication date.'))
        # Set the pub_date for published items if it hasn't been set already.
        if self.status == 'published' and self.pub_date is None:
            self.pub_date = datetime.date.today()


class Comment(models.Model):
    article = models.ForeignKey(Article, verbose_name=u"所属文章")
    parent_comment = models.ForeignKey('self', related_name='my_children', blank=True, null=True)
    # comment_choices = ((1,u'评论'),
    #               (2,u"点赞"))
    comment_type = models.IntegerField(default=1)
    user = models.ForeignKey("UserProfile")
    comment = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    comment_thumb_count = models.IntegerField(u"评论点赞数量", default=0)

    def clean(self):
        if self.comment_type == 1 and len(self.comment) == 0:
            raise ValidationError(u'评论内容不能为空，sb')

    def __str__(self):
        return "C:%s" % (self.comment)


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    brief = models.CharField(null=True, blank=True, max_length=255)
    set_as_top_menu = models.BooleanField(default=False)
    position_index = models.SmallIntegerField()
    admins = models.ManyToManyField("UserProfile", blank=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=32)
    signature = models.CharField(max_length=255, blank=True, null=True)
    head_img = models.ImageField(u"头像", blank=True, null=True, upload_to="statics/uploads",
                                 default='statics/uploads/no-img.jpg')
    article_like = models.ManyToManyField("Article", blank=True)
    # for web qq
    friends = models.ManyToManyField('self', related_name="my_friends", blank=True)

    def __str__(self):
        return self.name
