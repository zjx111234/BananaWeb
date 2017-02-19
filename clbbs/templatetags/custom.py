#!/usr/bin/env python
# -*- coding:utf-8 -*-


from django import template
from django.utils.html import format_html
import datetime,time,re

register = template.Library()


@register.filter
def truncate_url(img_obj):
    return img_obj.name.split("/")[-1]


@register.simple_tag
def filter_comment(article_obj):
    query_set = article_obj.comment_set.select_related()
    comments = {
        'comment_count': query_set.filter(comment_type=1).count(),
        #'thumb_count': query_set.filter(comment_type=2).count(),
    }
    return comments


@register.filter
def date_format(obj):
    if obj:
        now_datetime = datetime.datetime.now()
        now_datetime = now_datetime.strftime("%Y-%m-%d %H:%M:%S")
        pub_datetime = obj.strftime("%Y-%m-%d %H:%M:%S")
        now_datetime = re.split('-|:| ', now_datetime)
        pub_datetime = re.split('-|:| ', pub_datetime)
        time_diff = [int(now_datetime[i])-int(pub_datetime[i]) for i in range(len(pub_datetime))]
        if time_diff[0] > 0:
            return str(time_diff[0])+"年前"
        elif time_diff[1] > 0:
            return str(time_diff[1]) + "月前"
        elif time_diff[2] > 0:
            return str(time_diff[2]) + "天前"
        elif time_diff[3] > 0:
            return str(time_diff[3]) + "小时前"
        elif time_diff[4] > 0:
            return str(time_diff[4]) + "分钟前"
        else:
            return '刚刚'




