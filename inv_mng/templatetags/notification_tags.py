from django import template
from inv_mng.models import Notification  # Update with your app and model name

register = template.Library()

# This tag will return the unread notifications count for a user
@register.simple_tag
def unread_notifications_count(user):
    return Notification.objects.filter(user=user, is_read=False).count()
