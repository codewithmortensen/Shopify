from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from store.models import Customer


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_default_customer_profile(sender, **kwargs):
    if kwargs['created']:
        Customer.objects.create(customer=kwargs['instance'])
