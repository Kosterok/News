from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils import timezone

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    name = models.CharField(max_length=255, default = 'Иван')

    def __str__(self):
        return self.name

    def update_rating(self):
        posts_rating = self.post_set.aggregate(total=Sum('rating'))['total'] or 0
        posts_rating *= 3
        comments_auth_rating = self.user.comment_set.aggregate(total=Sum('rating'))['total'] or 0
        comments_to_posts_rating = Comment.objects.filter(post__author=self)\
                                   .aggregate(total=Sum('rating'))['total'] or 0
        self.rating = posts_rating + comments_auth_rating + comments_to_posts_rating
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=150, null=True, blank=True, db_index=True)
    subscribers = models.ManyToManyField(
        User, related_name="news_subscriptions", blank=True
    )
    def __str__(self):
        return self.name

class Post(models.Model):
    POST = 'PS'
    NEWS = 'NW'
    POST_TYPES = [(POST, 'Статья'), (NEWS, 'Новость')]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST_TYPES, default=NEWS)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)

    def like(self):
        self.rating += 1
        self.save(update_fields=['rating'])

    def dislike(self):
        self.rating -= 1
        self.save(update_fields=['rating'])

    def preview(self):
        return (self.text[:124] + '...') if len(self.text) > 124 else self.text
    def __str__(self):
        return f'{self.title.title()}: {self.text[:20]}'

    def get_absolute_url(self):
        return reverse('article_detail', args=[self.pk]) if self.post_type == self.POST \
               else reverse('news_detail', args=[self.pk])
    def clean(self):
        if self.post_type == self.NEWS and getattr(self, "author_id", None):
            today = timezone.localdate()
            cnt = Post.objects.filter(
                author=self.author,
                post_type=self.NEWS,
                created_at__date=today,
            ).exclude(pk=self.pk).count()
            if cnt >= 3:
                raise ValidationError('Лимит: не более 3 новостей в сутки.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save(update_fields=['rating'])

    def dislike(self):
        self.rating -= 1
        self.save(update_fields=['rating'])


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user