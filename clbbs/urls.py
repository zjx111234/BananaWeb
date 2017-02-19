from django.conf.urls import url
from clbbs import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^category/(\d+)/$', views.category),
    url(r'^article_detail/(\d+)/$', views.article_detail,name="article_detail"),
    url(r'^comment/$', views.comment, name="post_comment"),
    url(r'^get_comments/(\d+)', views.get_comments, name="get_comments"),
    url(r'^get_articles/(\d+)', views.get_articles, name="get_articles"),
    url(r'^new_article/$', views.new_article, name="new_article"),
    url(r'^register/$', views.register, name="register"),
    url(r'^user_center/(\d+)/$', views.register, name="user_center"),
    url(r'^get_new_article_num/$', views.get_new_article_num, name="get_new_article_num"),
    url(r'^add_favor/$', views.add_favor, name="add_favor"),
]
