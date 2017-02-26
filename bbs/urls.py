from django.conf.urls import url
from bbs import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^category/(\d+)/$', views.category),
    url(r'^article_detail/(\d+)/$', views.article_detail,name="article_detail"),
    url(r'^comment/$', views.comment, name="post_comment"),
    url(r'^get_comments/(\d+)', views.get_comments, name="get_comments"),
    url(r'^get_articles/(\d+)', views.get_articles, name="get_articles"),
    url(r'^new_article/$', views.new_article, name="new_article"),
    url(r'^register/$', views.register, name="register"),
    url(r'^get_new_article_num/$', views.get_new_article_num, name="get_new_article_num"),
    url(r'^add_favor/$', views.add_favor, name="add_favor"),
    url(r'^user_article/(\d+)$', views.user_article, name="user_article"),
    url(r'^user_comment/(\d+)$', views.user_comment, name="user_comment"),
    url(r'^user_draft/(\d+)$', views.user_draft, name="user_draft"),
    url(r'^user_draft/del_draft/(\d+)$', views.del_draft, name="del_draft"),
    url(r'^user_like_article/(\d+)$', views.user_like_article, name="user_like_article"),
    url(r'^user_detail/(\d+)$', views.user_comment_reply, name="user_detail"),
    url(r'^modify_draft/(\d+)$', views.modify_draft, name="modify_draft"),
    url(r'^modify_user_info/(\d+)$', views.modify_user_info, name="modify_user_info"),
    url(r'^modify_account/$', views.modify_account, name="modify_account"),
    url(r'^modify_head_img/(\d+)$', views.modify_head_img, name="modify_head_img"),
    url(r'^about/$', views.about_us, name="about"),
]
