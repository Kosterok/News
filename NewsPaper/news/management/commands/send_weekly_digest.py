# news/management/commands/send_weekly_digest.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from ...models import Category, Post


class Command(BaseCommand):
    help = 'Send weekly digest to subscribers'

    def handle(self, *args, **options):
        week_ago = timezone.now() - timedelta(days=7)

        for category in Category.objects.all():
            new_posts = Post.objects.filter(
                categories=category,
                created_at__gte=week_ago,
            )

            if new_posts.exists():
                subscribers = category.subscribers.all()

                for user in subscribers:
                    if user.email:
                        self.send_weekly_digest(user, category, new_posts)

    def send_weekly_digest(self, user, category, posts):
        subject = f'Еженедельный дайджест: новые статьи в категории "{category.name}"'

        message = render_to_string('emails/weekly_digest.html', {
            'user': user,
            'category': category,
            'posts': posts,
            'site_url': getattr(settings, "SITE_URL", "http://127.0.0.1:8000"),
            'week_start': timezone.now() - timedelta(days=7),
        })

        send_mail(
            subject=subject,
            message='',
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
