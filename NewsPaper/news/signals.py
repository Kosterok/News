# news/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from .tasks import send_post_created_notifications

@receiver(post_save, sender=Post)
def post_created_handler(sender, instance, created, **kwargs):
    if created:
        send_post_created_notifications.delay(instance.pk)
