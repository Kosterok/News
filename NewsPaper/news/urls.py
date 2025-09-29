from django.urls import path
from .views import PostsList, PostDetail  # или PostsList, как у тебя

urlpatterns = [
    path('', PostsList.as_view(), name='post_list'),
    path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
]