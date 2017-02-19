from django.shortcuts import render, HttpResponseRedirect, HttpResponse, render_to_response
from django.contrib.auth import login, logout, authenticate
from django import forms
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.core import serializers
from clbbs import models, form, add_articles_handler, comment_hander
import json, datetime, os, random
from PIL import Image
from BananaWeb import settings
# Create your views here.


category_list = models.Category.objects.filter(set_as_top_menu=True).order_by('position_index')


def index(request):
    #category_obj = models.Category.objects.get(position_index=1)
    articles_list = models.Article.objects.filter(status='published').order_by('priority')[0:6]
    article_count = models.Article.objects.count()
    return render(request,'bbs/index.html', {'category_list': category_list,
                                             'article_list': articles_list,
                                             'category_index': 1,
                                             'article_count': article_count
                                             })


def category(request, category_id):
    category_obj = models.Category.objects.get(id=category_id)
    if category_obj.position_index == 1:
        articles_list = models.Article.objects.filter(status='published').order_by('priority')[0:6]
        return render(request, 'bbs/index.html', {'category_list': category_list,
                                                  'article_list': articles_list,
                                                  'category_index': 1,
                                                  })
    elif category_obj.position_index == 2:
        articles_list = models.Article.objects.filter(status='published').order_by('pub_date').reverse()[0:6]
        return render(request, 'bbs/category.html', {'category_list': category_list,
                                                     'article_list': articles_list,
                                                     'category_obj': category_obj})
    else:
        articles_list = models.Article.objects.filter(status='published', category_id=category_id).order_by('priority')[0:6]
        return render(request, 'bbs/category.html', {'category_list': category_list,
                                                     'article_list': articles_list,
                                                     'category_obj': category_obj})


def acc_login(request):
    if request.method == 'POST':
        ret = {}
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None:
            #pass authentication
            login(request,user)
            ret['success'] = 'success'
            #return HttpResponseRedirect(request.GET.get('next') or '/clbbs')
            return HttpResponse(json.dumps(ret))
        else:
            #login_err = "Wrong username or password!"
            #return (request,'base.html', {'success':login_err})
            ret['success'] = 'failed'
            return HttpResponse(json.dumps(ret))
    return render(request,'index.html')


def acc_logout(request):
    logout(request)
    return HttpResponseRedirect('/clbbs')


def article_detail(request,article_id):
    article_obj = models.Article.objects.get(id=article_id)
    comment_tree = comment_hander.build_tree(article_obj.comment_set.select_related())
    return render(request,'bbs/article_detail.html', {'article_obj': article_obj,
                                                      'comment_tree': comment_tree,
                                                      'category_list': category_list})


def comment(request):
    print(request.POST)
    if request.method == 'POST':
        new_comment_obj = models.Comment(
            article_id=request.POST.get('article_id'),
            parent_comment_id=request.POST.get('parent_comment_id') or None,
            comment_type=request.POST.get("comment_type"),
            user_id=request.user.userprofile.id,
            comment=request.POST.get('comment')
        )
        new_comment_obj.save()
        return HttpResponse('post-comment-success')


def get_comments(request, article_id):
    article_obj = models.Article.objects.get(id=article_id)
    comment_tree = comment_hander.build_tree(article_obj.comment_set.select_related())
    tree_html = comment_hander.render_comment_tree(comment_tree)
    return HttpResponse(tree_html)


def get_articles(request, category_id):
    category_obj = models.Category.objects.get(id=category_id)
    if category_id == 1 or category_obj.position_index == 1:
        articles_list = models.Article.objects.filter(status='published').order_by('priority')
        ret = add_articles_handler.articles_generate_html(request, articles_list)
        return HttpResponse(json.dumps(ret))

    elif category_obj.position_index == 2:
        articles_list = models.Article.objects.filter(status='published').order_by('pub_date').reverse()
        ret = add_articles_handler.articles_generate_html(request, articles_list)
        return HttpResponse(json.dumps(ret))
    else:
        articles_list = models.Article.objects.filter(status='published', category_id=category_id).order_by('priority')
        ret = add_articles_handler.articles_generate_html(request, articles_list)
        return HttpResponse(json.dumps(ret))


def new_article(request):
    if request.method == 'GET':
        article_form = form.ArticleModelForm()
        return render(request,'bbs/new_article.html', {'article_form':article_form})
    elif request.method == 'POST':
        article_form = form.ArticleModelForm(request.POST,request.FILES)
        if article_form.is_valid():
            data = article_form.cleaned_data
            data['author_id'] = request.user.userprofile.id
            data['pub_date'] = datetime.datetime.now()
            article_obj = models.Article(**data)
            article_obj.save()
            return HttpResponseRedirect('/clbbs')
        else:
            return render(request,'bbs/new_article.html', {'article_form':article_form})


def register(request):
    error = []
    if request.method == 'POST':
        user_data = form.User(request.POST, request.FILES)
        if user_data.is_valid():
            username = user_data.cleaned_data['username']
            password1 = user_data.cleaned_data['password1']
            password2 = user_data.cleaned_data['password2']
            email = user_data.cleaned_data['email']
            nickname = user_data.cleaned_data['nickname']
            if not models.User.objects.filter(username=username):
                if not models.UserProfile.objects.filter(name=nickname):
                    if user_data.pwd_validate(password1, password2):
                        user_obj = models.User.objects.create(username=username, email=email)
                        user_obj.set_password(password2)
                        user_obj.save()
                        if request.FILES['head_img']:
                            head_img = request.FILES['head_img']
                            small_head_img = Image.open(head_img)
                            small_head_img.thumbnail((30, 30), Image.ANTIALIAS)
                            url = 'uploads/'+head_img.name
                            name = settings.STATICFILES_DIRS[0]+ '/' + url
                            if os.path.exists(name):
                                file, ext = os.path.splitext(head_img.name)
                                file = file + str(random.randint(1, 1000))
                                head_img.name = file + ext
                                url = 'uploads/' + head_img.name
                                name = settings.STATICFILES_DIRS[0] + '/' + url
                            small_head_img.save(name, "png")
                        user_profile_obj = models.UserProfile.objects.create(user=user_obj, name=nickname, head_img=url)
                        user_profile_obj.save()
                        user = authenticate(username=username,
                                            password=password1)
                        login(request,user)
                        return HttpResponseRedirect('/clbbs')
                    else:
                        user_form = user_data
                        error.append('请输入相同密码')
                else:
                    user_form = user_data
                    error.append('此昵称已经存在')
            else:
                user_form = user_data
                error.append('用户名已存在')
    else:
        user_form = form.User
    return render(request, 'bbs/register.html', {'user_form': user_form,
                                                 'error': error
                                                })


def user_center(request, user_id):
    pass


def get_new_article_num(request):
    page_article_num = request.GET.get('last_num')
    if page_article_num:
        db_article_num = models.Article.objects.count()
        new_article_num = db_article_num-int(page_article_num)
    else:
        new_article_num = 0
    return HttpResponse(json.dumps({'new_article_num': new_article_num}))


def add_favor(request):
    ret = {'status': '', 'data': '', 'message': ''}
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        user_name = request.POST.get('user_name')

        article_obj = models.Article.objects.get(id=article_id)
        user_obj = models.UserProfile.objects.get(name=user_name)
        user_like_article = user_obj.article_like.all()
        if article_obj not in user_like_article:
            article_like_obj = models.Article.objects.filter(id__in=[article_id])
            user_obj.article_like.add(*article_like_obj)
            thumb_num = article_obj.thumb_count + 1
            article_obj.thumb_count = thumb_num
            priority = article_obj.priority + 10
            article_obj.priority = priority
            article_obj.save()
            ret['status'] = 'success'
            ret['data'] = thumb_num
        else:
            ret['status'] = 'fail'
    return HttpResponse(json.dumps(ret))

'''
class CJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H-%M-%S")
        elif isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, o)
'''