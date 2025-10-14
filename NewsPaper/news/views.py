from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Category, Author
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape
from django.utils.text import Truncator
from django.conf import settings
from django.core.exceptions import ValidationError

class PostTypeMixin:
    post_type = None

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(post_type=self.post_type) if self.post_type else qs

class PostsList(PostTypeMixin, ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        # важно вызывать super(), чтобы не сломать фильтрацию из PostTypeMixin
        return super().get_queryset().prefetch_related('categories')

class PostDetail(PostTypeMixin, DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельному товару
    model = Post
    # Используем другой шаблон — product.html
    template_name = 'post.html'
    # Название объекта, в котором будет выбранный пользователем продукт
    context_object_name = 'post'

class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    post_type = None

    def form_valid(self, form):
        post = form.save(commit=False)
        author, _ = Author.objects.get_or_create(user=self.request.user)
        post.author = author
        if self.post_type:
            post.post_type = self.post_type
        try:
            post.full_clean()
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        return super().form_valid(form)

class ArticlesCreate(LoginRequiredMixin, PostCreate):
    permission_required = ('news.add_post',)
    post_type = 'PS'

class ArticleUpdate(LoginRequiredMixin,PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('posts')

class ArticleDelete(LoginRequiredMixin, PermissionRequiredMixin,  DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts')

class NewsCreate(LoginRequiredMixin, PostCreate):
    permission_required = ('news.add_post',)
    post_type = 'NW'

class NewsUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('posts')

class NewsDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts')

class PostSearch(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'search.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'account/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context

@login_required
def upgrade_me(request):
    user = request.user
    premium_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        premium_group.user_set.add(user)
    return redirect('/')


@login_required
def toggle_subscription(request, pk):
    category = get_object_or_404(Category, pk=pk)
    u = request.user
    if request.method == "POST":
        if category.subscribers.filter(id=u.id).exists():
            category.subscribers.remove(u)
        else:
            category.subscribers.add(u)
    return redirect(request.META.get("HTTP_REFERER") or "/")