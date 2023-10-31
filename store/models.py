from django.db import models
from django.core.validators import MinLengthValidator
from Shopify.settings import AUTH_USER_MODEL


class Customer(models.Model):
    customer = models.OneToOneField(
        AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    membership_gold = 'G'
    membership_silver = 'S'
    membership_bronze = 'B'

    membership_status = [
        (membership_bronze, 'Bronze'),
        (membership_silver, 'Silver'),
        (membership_gold, 'Gold')
    ]

    membership = models.CharField(
        max_length=1, choices=membership_status, default=membership_bronze)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['customer__first_name', 'customer__last_name']
