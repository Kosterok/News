from django.contrib import admin
from django.urls import path
from django.urls import include
from .views import (PostsList, PostDetail, PostSearch,
                    ArticlesCreate, ArticleUpdate, ArticleDelete,
                    NewsCreate, NewsUpdate, NewsDelete,
                    )
from .views import IndexView, upgrade_me
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .views import PostCreate, toggle_subscription

urlpatterns = [
    path('', PostsList.as_view(), name='posts'),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', IndexView.as_view(), name='profile'),
    path('sign/upgrade/', upgrade_me, name='become_author'),

    path('articles/', PostsList.as_view(post_type='PS'), name='article_list'),
    path('news/', PostsList.as_view(post_type='NW'), name='news_list'),

    # детальные страницы
    path('articles/<int:pk>/', PostDetail.as_view(post_type='PS'), name='article_detail'),
    path('news/<int:pk>/', PostDetail.as_view(post_type='NW'), name='news_detail'),

    path('search/', PostSearch.as_view(), name='post_search'),
    path('articles/create/', ArticlesCreate.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', ArticleUpdate.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', ArticleDelete.as_view(), name='article_delete'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', NewsUpdate.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
    path("category/<int:pk>/subscribe/", toggle_subscription, name="toggle_sub"),


]