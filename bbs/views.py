from django.shortcuts import render, HttpResponseRedirect, HttpResponse, render_to_response
from django.contrib.auth import login, logout, authenticate
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from bbs import models, form, add_articles_handler, comment_hander
import json, datetime, os, random
from PIL import Image
from BananaWeb import settings

# Create your views here.


category_list = models.Category.objects.filter(set_as_top_menu=True).order_by('position_index')


def index(request):
    # category_obj = models.Category.objects.get(position_index=1)
    articles_list = models.Article.objects.filter(status='published').order_by('-priority')[0:6]
    article_count = models.Article.objects.filter(status='published').count()
    return render(request, 'bbs/index.html', {'category_list': category_list,
                                              'article_list': articles_list,
                                              'category_index': 1,
                                              'article_count': article_count,
                                              })


def category(request, category_id):
    category_obj = models.Category.objects.get(id=category_id)
    if category_obj.position_index == 1:
        articles_list = models.Article.objects.filter(status='published').order_by('-priority')[0:6]
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
        articles_list = models.Article.objects.filter(status='published', category_id=category_id).order_by(
            '-priority')[0:6]
        return render(request, 'bbs/category.html', {'category_list': category_list,
                                                     'article_list': articles_list,
                                                     'category_obj': category_obj})


def acc_login(request):
    if request.method == 'POST':
        ret = {}
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            ret['success'] = 'success'
            request.session['user_comment_count'] = 0
            request.session['user_login_time'] = datetime.datetime.now().strftime("%H %M %S")
            return HttpResponse(json.dumps(ret))
        else:
            ret['success'] = 'failed'
            return HttpResponse(json.dumps(ret))
    return HttpResponseRedirect('/bbs')


def acc_logout(request):
    logout(request)
    return HttpResponseRedirect('/bbs')


def article_detail(request, article_id):
    article_obj = models.Article.objects.get(id=article_id)
    author_id = article_obj.author.id
    author_article_num = models.Article.objects.filter(id=author_id).count()
    author_comment_num = models.Comment.objects.filter(id=author_id).count()
    if not author_comment_num:
        author_comment_num = 0
    click_count = article_obj.click_count
    article_obj.click_count = click_count + 1
    priority = article_obj.priority + 1
    article_obj.priority = priority
    article_obj.save()
    comment_tree = comment_hander.build_tree(article_obj.comment_set.select_related())
    return render(request, 'bbs/article_detail.html', {'article_obj': article_obj,
                                                       'comment_tree': comment_tree,
                                                       'category_list': category_list,
                                                       'author_article_num': author_article_num,
                                                       'author_comment_num': author_comment_num
                                                       })


def comment(request):
    if request.method == 'POST':
        if 'first_comment_time' not in request.session or request.session['user_comment_count'] < 5:
            request.session['first_comment_time'] = datetime.datetime.now().strftime("%H %M %S")
            new_comment_obj = models.Comment(
                article_id=request.POST.get('article_id'),
                parent_comment_id=request.POST.get('parent_comment_id') or None,
                comment_type=request.POST.get("comment_type"),
                user_id=request.user.userprofile.id,
                comment=request.POST.get('comment')
            )
            user_obj = models.UserProfile.objects.get(id=request.user.userprofile.id)
            experience = user_obj.experience + 10
            user_obj.experience = experience
            user_obj.save()
            new_comment_obj.save()
            user_comment_count = request.session['user_comment_count'] + 1
            request.session['user_comment_count'] = user_comment_count
            return HttpResponse('post-comment-success')
        else:
            now_time = datetime.datetime.now().strftime("%H %M %S").split(' ')
            session_time = request.session['first_comment_time'].split(' ')
            time_diff = (int(now_time[0]) - int(session_time[0])) * 3600 + (int(now_time[1]) - int(
                session_time[1])) * 60 + (int(now_time[2]) - int(session_time[2]))
            if time_diff < 60:
                return HttpResponse('comment-num-out')
            elif time_diff > 60:
                del request.session['first_comment_time']
                request.session['user_comment_count'] = 0
                new_comment_obj = models.Comment(
                    article_id=request.POST.get('article_id'),
                    parent_comment_id=request.POST.get('parent_comment_id') or None,
                    comment_type=request.POST.get("comment_type"),
                    user_id=request.user.userprofile.id,
                    comment=request.POST.get('comment')
                )
                user_obj = models.UserProfile.objects.get(id=request.user.userprofile.id)
                experience = user_obj.experience + 10
                user_obj.experience = experience
                article_obj = models.Article.objects.get(id=request.POST.get('article_id'))
                priority = article_obj.priority + 5
                article_obj.priority = priority
                article_obj.save()
                user_obj.save()
                new_comment_obj.save()
                user_comment_count = request.session['user_comment_count'] + 1
                request.session['user_comment_count'] = user_comment_count
                request.session['first_comment_time'] = datetime.datetime.now().strftime("%H %M %S")
                return HttpResponse('post-comment-success')
    return HttpResponseRedirect(request.path)


def get_comments(request, article_id):
    article_obj = models.Article.objects.get(id=article_id)
    comment_tree = comment_hander.build_tree(article_obj.comment_set.select_related())
    tree_html = comment_hander.render_comment_tree(comment_tree)
    return HttpResponse(tree_html)


def get_articles(request, category_id):
    category_obj = models.Category.objects.get(id=category_id)
    if category_id == 1 or category_obj.position_index == 1:
        articles_list = models.Article.objects.filter(status='published').order_by('-priority')
        ret = add_articles_handler.articles_generate_html(request, articles_list)
        return HttpResponse(json.dumps(ret))

    elif category_obj.position_index == 2:
        articles_list = models.Article.objects.filter(status='published').order_by('pub_date').reverse()
        ret = add_articles_handler.articles_generate_html(request, articles_list)
        return HttpResponse(json.dumps(ret))
    else:
        articles_list = models.Article.objects.filter(status='published', category_id=category_id).order_by('-priority')
        ret = add_articles_handler.articles_generate_html(request, articles_list)
        return HttpResponse(json.dumps(ret))


@login_required
def new_article(request):
    if request.method == 'GET':
        article_form = form.ArticleModelForm()
        return render(request, 'bbs/new_article.html', {'article_form': article_form})
    elif request.method == 'POST':
        article_form = form.ArticleModelForm(request.POST, request.FILES)
        if article_form.is_valid():
            data = article_form.cleaned_data
            data['author_id'] = request.user.userprofile.id
            data['pub_date'] = datetime.datetime.now()
            article_obj = models.Article(**data)
            user_obj = models.UserProfile.objects.get(id=data['author_id'])
            experience = user_obj.experience + 100
            user_obj.experience = experience
            user_obj.save()
            article_obj.save()
            return HttpResponseRedirect('/bbs')
        else:
            return render(request, 'bbs/new_article.html', {'article_form': article_form})


def image_handler(img_cls):
    url = ''
    if img_cls:
        head_img = img_cls
        small_head_img = Image.open(head_img)
        small_head_img.thumbnail((150, 150), Image.ANTIALIAS)
        url = 'uploads/' + head_img.name
        name = settings.STATICFILES_DIRS[0] + '/' + url
        if os.path.exists(name):
            file, ext = os.path.splitext(head_img.name)
            file = file + str(random.randint(1, 1000))
            head_img.name = file + ext
            url = 'uploads/' + head_img.name
            name = settings.STATICFILES_DIRS[0] + '/' + url
        small_head_img.save(name, "png")
    return url


def register(request):
    if request.method == 'GET':
        user_form = form.UserForm
        return render(request, 'bbs/register.html', {'user_form': user_form})
    if request.method == 'POST':
        user_data = form.UserForm(request.POST, request.FILES)
        if user_data.is_valid():
            username = user_data.cleaned_data['username']
            password2 = user_data.cleaned_data['password2']
            sign_up_time = datetime.datetime.now()
            email = user_data.cleaned_data['email']
            nickname = user_data.cleaned_data['nickname']
            user_obj = models.User.objects.create(username=username, email=email)
            user_obj.set_password(password2)
            user_obj.save()
            url = image_handler(request.FILES['head_img'])
            user_profile_obj = models.UserProfile.objects.create(user=user_obj, name=nickname, head_img=url,
                                                                 sign_up_time=sign_up_time)
            user_profile_obj.save()
            user = authenticate(username=username, password=password2)
            login(request, user)
            request.session['user_comment_count'] = 0
            request.session['user_login_time'] = datetime.datetime.now().strftime("%H %M %S")
            return HttpResponseRedirect('/bbs')
        user_form = user_data
        return render(request, 'bbs/register.html', {'user_form': user_form,
                                                     })


def get_new_article_num(request):
    page_article_num = request.GET.get('last_num')
    if page_article_num:
        db_article_num = models.Article.objects.count()
        new_article_num = db_article_num - int(page_article_num)
    else:
        new_article_num = 0
    return HttpResponse(json.dumps({'new_article_num': new_article_num}))


@login_required
def add_favor(request):
    ret = {'status': '', 'data': '', 'message': ''}
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        user_name = request.POST.get('user_name')
        article_obj = models.Article.objects.get(id=article_id)
        user_obj = models.UserProfile.objects.get(name=user_name)
        user_like_articles = user_obj.article_like.all()
        if article_obj not in user_like_articles:
            article_like_obj = models.Article.objects.filter(id__in=[article_id])
            user_obj.article_like.add(*article_like_obj)
            experience = user_obj.experience + 5
            user_obj.experience = experience
            user_obj.save()
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


def user_information(request, user_id):
    user_obj = models.UserProfile.objects.get(id=user_id)
    experience = user_obj.experience
    if experience >= 300:
        user_obj.user_level = '香蕉皮'
    elif experience >= 1000:
        user_obj.user_level = '小香蕉'
    elif experience >= 2000:
        user_obj.user_level = '大香蕉'
    elif experience >= 3000:
        user_obj.user_level = '皮皮香焦'
    elif experience >= 5000:
        user_obj.user_level = '宇宙无敌大香蕉'
    user_obj.save()
    user_info = models.UserProfile.objects.get(id=user_id)
    return user_info


def user_article(request, user_id):
    publish_article_list = models.Article.objects.filter(author__id=user_id).order_by('pub_date')
    one_page_articles = add_articles_handler.page_handler(request, publish_article_list)
    user_info = user_information(request, user_id)
    return render(request, 'bbs/user_articles.html', {'publish_article_list': one_page_articles,
                                                      'user_info': user_info,
                                                      'current_user_id': user_id})


def user_comment(request, user_id):
    user_comments = models.Comment.objects.filter(user_id=user_id)
    comment_count = models.Comment.objects.filter(user_id=user_id).count()
    one_page_comment = add_articles_handler.page_handler(request, user_comments)
    # comment_article_list = models.Article.objects.filter(comment__user_id=user_id).order_by('pub_date')
    user_info = user_information(request, user_id)
    return render(request, 'bbs/user_comment.html', {'comment_list': one_page_comment,
                                                     'user_info': user_info,
                                                     'comment_count': comment_count,
                                                     'current_user_id': user_id})


def user_draft(request, user_id):
    draft_list = models.Article.objects.filter(status='draft', author__id=user_id).order_by('pub_date')
    one_page_draft = add_articles_handler.page_handler(request, draft_list)
    user_info = user_information(request, user_id)
    return render(request, 'bbs/user_draft.html', {'draft_list': one_page_draft,
                                                   'user_info': user_info,
                                                   'current_user_id': user_id
                                                   })


@login_required
def modify_draft(request, draft_id):
    if request.method == 'GET':
        draft = models.Article.objects.get(id=draft_id)
        data = model_to_dict(draft)
        article_form = form.ArticleModelForm(data)
        return render(request, 'bbs/new_article.html', {'article_form': article_form})
    elif request.method == 'POST':
        article_form = form.ArticleModelForm(request.POST, request.FILES)
        if article_form.is_valid():
            data = article_form.cleaned_data
            data['author_id'] = request.user.userprofile.id
            data['pub_date'] = datetime.datetime.now()
            article_obj = models.Article(**data)
            user_obj = models.UserProfile.objects.get(id=data['author_id'])
            experience = user_obj.experience + 100
            user_obj.experience = experience
            models.Article.objects.get(id=draft_id).delete()
            article_obj.save()
            user_obj.save()
            return HttpResponseRedirect('/bbs')
        else:
            return render(request, 'bbs/new_article.html', {'article_form': article_form})


def del_draft(request, article_id):
    if request.method == 'GET':
        try:
            models.Article.objects.get(id=article_id).delete()
            return HttpResponse('success')
        except Exception as e:
            return HttpResponse(e)


def user_like_article(request, user_id):
    user_obj = models.UserProfile.objects.get(id=user_id)
    user_like_articles = user_obj.article_like.all().order_by('pub_date')
    one_page_like_articles = add_articles_handler.page_handler(request, user_like_articles)
    user_info = user_information(request, user_id)
    return render(request, 'bbs/user_like_articles.html', {'user_like_articles': one_page_like_articles,
                                                           'current_user_id': user_id,
                                                           'user_info': user_info,
                                                           })


def user_comment_reply(request, user_id):
    user_comments = models.Comment.objects.filter(user_id=user_id).order_by('date').reverse()
    user_info = user_information(request, user_id)
    comment_article_title_list = [models.Article.objects.get(id=obj.article_id).title for obj in user_comments]
    comment_dict = {}
    comment_reply = {}
    for comment_article_title in comment_article_title_list:
        for comment_obj in user_comments:
            tmp = {}
            reply_list = []
            reply = models.Comment.objects.filter(parent_comment_id=comment_obj.id)
            for content in reply:
                reply_list.append(content.user.name + ':' + content.comment)
            if reply:
                article_name = models.Article.objects.get(id=comment_obj.article_id).title
                if article_name == comment_article_title:
                    tmp[comment_obj.comment] = reply_list
                    comment_dict.update(tmp)
        if comment_dict:
            comment_reply[comment_article_title] = comment_dict
        comment_dict = {}
    return render(request, 'bbs/user_detail.html', {'comment_reply': comment_reply,
                                                    'user_info': user_info,
                                                    'current_user_id': user_id
                                                    })


@login_required
def modify_user_info(request, user_id):
    if request.method == 'GET':
        user_info = models.UserProfile.objects.get(id=user_id)
        data = model_to_dict(user_info)
        user_info_form = form.UserProfileModelForm(data)
        return render(request, 'bbs/modify_info.html', {'user_info_form': user_info_form})

    if request.method == 'POST':
        error = []
        user_info_form = form.UserProfileModelForm(request.POST)
        if user_info_form.is_valid():
            nickname = user_info_form.cleaned_data['name']
            user_profile_obj = models.UserProfile.objects.filter(id=user_id)
            user_profile_get_obj = models.UserProfile.objects.get(id=user_id)
            current_name = user_profile_get_obj.name
            if nickname != current_name and models.UserProfile.objects.filter(name=nickname):
                print(nickname, current_name)
                error.append('此昵称已经存在')
                return render(request, 'bbs/modify_info.html', {'user_info_form': user_info_form,
                                                                'error': error
                                                                })
            else:
                data = user_info_form.cleaned_data
                user_profile_obj.update(**data)
                user_profile_get_obj.refresh_from_db()
                return HttpResponseRedirect('/bbs')
        else:
            return render(request, 'bbs/modify_info.html', {'user_info_form': user_info_form,
                                                            })


@login_required
def modify_account(request):
    if request.method == 'GET':
        password_form = form.ChangePwdForm()
        return render(request, 'bbs/modify_account.html', {'password_form': password_form, })
    else:
        password_form = form.ChangePwdForm(request.POST)
        if password_form.is_valid():
            username = request.user.username
            old_password = request.POST.get('old_password', '')
            user = authenticate(username=username, password=old_password)
            new_password = request.POST.get('new_password1', '')
            user.set_password(new_password)
            user.save()
            return HttpResponseRedirect('/bbs')
    return render(request, 'bbs/modify_account.html', {'password_form': password_form, })


@login_required
def modify_head_img(request, user_id):
    head_img_form = form.UserHeadImgForm()
    if request.method == 'POST':
        formset = form.UserHeadImgForm(request.POST, request.FILES)
        if formset.is_valid():
            user_head_img = models.UserProfile.objects.get(id=user_id)
            user_head_img.head_img = formset.cleaned_data['head_img']
            user_head_img.save()
            return HttpResponseRedirect('/bbs')
    else:
        head_img_form = head_img_form
    return render(request, "bbs/modify_head_img.html", {"head_img_form": head_img_form, })


def about_us(request):
    return render_to_response('bbs/about.html', {})


'''
class CJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime("%H %M %S")
        elif isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, o)
'''
