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


class Address(models.Model):
    city = models.CharField(max_length=255, validators=[MinLengthValidator(3)])
    street = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3)]
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='address')

    def __str__(self) -> str:
        return f'{self.street} - {self.city}'


class Promotion(models.Model):
    title = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3)]
    )
    slug = models.SlugField()
    description = models.TextField()
    discount = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title', 'end_date', 'start_date']
        indexes = [
            models.Index(fields=['title', 'discount']),
            models.Index(fields=['start_date', 'end_date'])
        ]


class Collection(models.Model):
    title = models.CharField(
        max_length=255, validators=[MinLengthValidator(3)]
    )
    slug = models.SlugField()
    # featured_product = models.ForeignKey(
    #     "Product", on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    promotion = models.ForeignKey(
        Promotion, on_delete=models.SET_NULL, related_name='collection', null=True, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']
