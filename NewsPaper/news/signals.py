from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models.signals import m2m_changed
from django.utils.html import escape
from django.utils.text import Truncator
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Post

@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers_on_category_add(sender, instance: Post, action, pk_set, **kwargs):
    if action != 'post_add':
        return
    if instance.post_type != Post.NEWS or not getattr(instance, "is_published", True):
        return
    if not pk_set:
        return

    users = (
        instance.categories.filter(pk__in=pk_set)
        .values_list("subscribers__username", "subscribers__email")
        .distinct()
    )
    recipients = [(u, e) for (u, e) in users if e]

    if not recipients:
        return

    title = instance.title
    preview = Truncator(instance.text).chars(200, truncate="…")

    site = getattr(settings, "SITE_URL", "http://localhost:8000")
    url = f"{site}{instance.get_absolute_url()}"
    subject = f"Новая новость: {title}"

    def _send():
        for username, email in recipients:
            text = (
                f"{title}\n"
                f"{preview}\n"
                f"Здравствуй, {username}. Появилась новая публикация в подписанных разделах.\n"
                f"Читать полностью: {url}"
            )
            html = (
                f"<h1>{escape(title)}</h1>"
                f"<p>{escape(preview)}</p>"
                f"<p>Здравствуй, {escape(username)}. "
                f"Появилась новая публикация в подписанных разделах.</p>"
                f"<p><a href=\"{escape(url)}\">Читать полностью</a></p>"
            )
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                to=[email],
            )
            msg.attach_alternative(html, "text/html")
            msg.send()

    transaction.on_commit(_send)

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and instance.email:
        subject = "Добро пожаловать на сайт!"
        message = (
            f"Здравствуйте, {instance.username}!\n\n"
            f"Вы успешно зарегистрировались на сайте {settings.SITE_URL}.\n\n"
            "Рады видеть вас среди наших пользователей!"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=False,
        )