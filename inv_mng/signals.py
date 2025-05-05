from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Stock, Notification, Item

@receiver(post_save, sender=Stock)
def check_stock_threshold(sender, instance, **kwargs):
    """Creates a notification if the stock entry falls below the minimum threshold."""
    print("Instance ID")
    print(instance.item_id.pk)
    stock_item = instance.item_id.pk
    item = Item.objects.get(item_id=stock_item)
    min_threshold = item.minimum_quantity  # Fetch the correct threshold
    print(min_threshold)

    if instance.total_quantity < min_threshold:
        staff_users = User.objects.filter(is_staff=True)
        for user in staff_users:
            Notification.objects.get_or_create(
                user=user,
                stock_entry=instance,
                message=f"Warning: Stock for {instance.item_id} (Vendor: {instance.vendor}, Expiry: {instance.expiry_date}) is below the threshold ({instance.total_quantity} left)."
            )
