from django.urls import path
from .views import (PostsList, PostDetail, PostSearch,
                    ArticlesCreate, ArticleUpdate, ArticleDelete,
                    NewsCreate, NewsUpdate, NewsDelete,
                    )

urlpatterns = [
    path('', PostsList.as_view(), name='posts'),
    # списки (если нужны)
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


]