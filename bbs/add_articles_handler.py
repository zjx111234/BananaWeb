# -*- coding:utf-8 -*-
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from bbs.templatetags import custom
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, render_to_response
from bbs import views


def page_handler(re, obj_list):
    ret = {'type': 'json'}
    page_cls = Paginator(obj_list, 6)
    if re.method == 'POST':
        page_num = re.POST.get('page_num')
        try:
            contents = page_cls.page(page_num)
            ret['page_num'] = str(int(page_num) + 1)
            ret['data'] = contents
            ret['success'] = 'success'

        except EmptyPage:
            contents = page_cls.page(page_cls.num_pages)
            ret['success'] = 'fail-forward'
            ret['page_num'] = str(int(page_num) + 1)
            ret['data'] = contents
        return ret
    else:
        page = re.GET.get('page')
        try:
            contents = page_cls.page(page)
        except PageNotAnInteger:
            contents = page_cls.page(1)
        except EmptyPage:
            contents = page_cls.page(page_cls.num_pages)
        return contents


def articles_generate_html(re, obj_list):
    html = ''
    articles = page_handler(re, obj_list)
    if articles['success'] == 'failed':
        articles['data'] = html
        return articles
    for obj in articles['data']:
        img_name = custom.truncate_url(obj.head_img)
        comments = custom.filter_comment(obj)
        pub_date = custom.date_format(obj.pub_date)
        comment_count = str(comments['comment_count'])
        thumb_count = obj.thumb_count
        img_a = "<a href='/bbs/article_detail/" + str(obj.id) + " ' target='_blank'>"
        ele = "<div article_id='%d' class='article-box'>" % obj.id + \
              "<div class='article-head-img col-md-4' style='padding-left: 0px;'>" + img_a + \
              " <img src='/static/uploads/%s' >" % img_name + "</div></a>" + \
              "<div class='article-brief col-md-8'><a class='article-title' href='/bbs/article_detail/" + str(obj.id) + \
              "' target='_blank' >" + "%s</a>" % obj.title + \
              "<div class ='article-brief-info' ><a href='/bbs/user_comment/" + str(obj.author.id) + \
              "' class='author-name' target='_blank' >%s</a > " % obj.author.name + \
              "<span class='time' >%s</span>" % pub_date + \
              "<i class='icon icon-cmt'></i><em>%s</em>" % comment_count + \
              "<i class='icon icon-fvr'></i><em>%s</em></div>" % thumb_count + \
              "<div class='article-brief-text'><p>%s</p></div></div></div>" % obj.brief
        html += ele
    articles['data'] = html
    return articles


def short_articles_generate_html(re, obj_list):
    html = ''
    short_articles = page_handler(re, obj_list)
    if short_articles['success'] == 'failed':
        short_articles['data'] = html
        return short_articles
    for obj in short_articles['data']:
        pub_date = custom.date_format(obj.pub_date)
        thumb_count = obj.thumb_count
        ele = "<li><div class='story-content'><div class='story-title' story-data-show='false' onclick='Hidden(this,%d);'>" % obj.id + \
              "<p class='transition'><span class='icon icon-caret'></span>%s</p>" % obj.title + \
              "</div><div class='story-info' id='short%s' style='display:none;'>" % str(obj.id) + \
              "<p class='story-detail-hide'>%s</p>" % obj.content + \
              "<div class='story-time'><p class='like'></p><div class='article-type pull-right'><div class='icon-like-prompt'></div>" + \
              "<ul><li class='js-icon-like-new load-count-list' data-type='like'><i class='icon icon-like' onclick='add_thumb(this,%d);'></i>" % obj.id + \
              "<span class='like agree-count'>%s</span></li></ul></div><p></p><div class='clear'></div></div></div>" % thumb_count + \
              "<div class='story-time story-time-footer'><p class='time'>%s</p>" % pub_date + \
              "<p class='short-tag'>%s</p><div class='clear'></div></div></div></li>" % obj.tag
        html += ele
    short_articles['data'] = html
    return short_articles
