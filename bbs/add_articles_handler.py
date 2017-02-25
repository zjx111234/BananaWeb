# -*- coding:utf-8 -*-
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from bbs.templatetags import custom
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, render_to_response
from bbs import views

'''

def page_handler(re, obj_list):
    ret = {'type':'json'}
    page_cls = Paginator(obj_list, 4)
    if re.method == 'POST':
        page_num = re.POST.get('page_num')
        try:
            contents = [model_to_dict(i) for i in page_cls.page(page_num).object_list]
            for values in contents:
                values['head_img'] = values['head_img'].url
            ret['data'] = contents
            ret['success'] = 'success'
            ret['msg'] = ''
        except PageNotAnInteger:
            contents = page_cls.page(1)
            ret['success'] = 'fail'
            ret['msg'] = PageNotAnInteger
            ret['data'] = contents
        except EmptyPage:
            contents = page_cls.page(page_cls.num_pages)
            ret['success'] = 'fail'
            ret['msg'] = EmptyPage
            ret['data'] = contents
        return json.dumps(ret, cls=CJsonEncoder)
    else:
        page = re.GET.get('page')
        try:
            contents = page_cls.page(page)
        except PageNotAnInteger:
            contents = page_cls.page(1)
        except EmptyPage:
            contents = page_cls.page(page_cls.num_pages)
        return contents


'''


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
        img_a = "<a href='/bbs/article_detail/" + str(obj.id) + " '>"
        ele = "<div article_id='%d' class='article-box'>" % obj.id + \
              "<div class='article-head-img col-md-4' style='padding-left: 0px;'>" + img_a + \
              " <img src='/static/uploads/%s'>" % img_name + "</div></a>" + \
              "<div class='article-brief col-md-8'><a class='article-title' href='/bbs/article_detail/" + str(obj.id) +\
              "'>" + "%s</a>" % obj.title + \
              "<div class ='article-brief-info' ><a href='/bbs/user_detail/" + str(obj.author.id) + \
              "' class='author-name'>%s</a > " % obj.author.name + \
              "<span class='time' >%s</span>" % pub_date + \
              "<i class='icon icon-cmt'></i><em>%s</em>" % comment_count + \
              "<i class='icon icon-fvr'></i><em>%s</em></div>" % thumb_count + \
              "<div class='article-brief-text'><p>%s</p></div></div></div>" % obj.brief
        html += ele
    articles['data'] = html
    print(articles)
    return articles


'''
        except PageNotAnInteger:
            contents = page_cls.page(1)
            ret['success'] = 'fail-back'
            ret['page_num'] = str(int(page_num) + 1)
            ret['data'] = contents


'''
