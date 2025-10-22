from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from django.urls import reverse

#Рассылка сразу после создания новости
@shared_task(bind=True)
def send_post_created_notifications(self, post_id: int):

    from .models import Post, Category

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return f"Пост id={post_id} не найден"

    categories = post.categories.all()
    if not categories.exists():
        return f"У поста {post_id} нет категорий"
    subscribers_emails = set()
    for category in categories:
        for user in category.subscribers.all():
            if user.email:
                subscribers_emails.add(user.email)

    if not subscribers_emails:
        return "Подписчиков нет — уведомления не отправлены."

    context = {
        "post": post,
        "site_url": "http://127.0.0.1:8000",
    }
    html_body = render_to_string("emails/news_created.html", context)
    text_body = strip_tags(html_body)

    msg = EmailMultiAlternatives(
        subject=f"Новая публикация: {post.title}",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=list(subscribers_emails),
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()

    return f"Отправлено {len(subscribers_emails)} уведомлений подписчикам."


#Еженедельная рассылка
@shared_task(bind=True)
def send_weekly_digest(self):

    from .models import Post, Category

    now = timezone.now()
    week_ago = now - timedelta(days=7)
    recent_posts = Post.objects.filter(created_at__gte=week_ago, is_published=True)

    if not recent_posts.exists():
        return "За последнюю неделю нет новых постов."

    # группируем посты по категориям
    posts_by_category = defaultdict(list)
    for post in recent_posts:
        for category in post.categories.all():
            posts_by_category[category].append(post)

    total_sent = 0
    for category, posts in posts_by_category.items():
        subscribers = category.subscribers.all()
        if not subscribers.exists():
            continue

        for subscriber in subscribers:
            if not subscriber.email:
                continue

            context = {
                "user": subscriber,
                "category": category,
                "posts": posts,
                "site_url": "http://127.0.0.1:8000",
            }
            html_body = render_to_string("emails/weekly_digest.html", context)
            text_body = strip_tags(html_body)

            msg = EmailMultiAlternatives(
                subject=f"Еженедельный дайджест по категории: {category.name}",
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email],
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()
            total_sent += 1

    return f"Еженедельная рассылка отправлена {total_sent} пользователям."
