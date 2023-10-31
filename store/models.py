from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from Shopify.settings import AUTH_USER_MODEL
from decimal import Decimal
from django.utils import timezone
from django.contrib import admin
from uuid import uuid4


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

    @admin.display(ordering='customer__first_name')
    def first_name(self):
        return self.customer.first_name

    @admin.display(ordering='customer__last_name')
    def last_name(self):
        return self.customer.last_name

    @admin.display(ordering='customer__email')
    def email(self):
        return self.customer.email

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
    featured_product = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    promotion = models.ForeignKey(
        Promotion, on_delete=models.SET_NULL, related_name='collection', null=True, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']


class Product(models.Model):
    title = models.CharField(
        max_length=255, validators=[MinLengthValidator(3)]
    )
    slug = models.SlugField()
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    last_update = models.DateTimeField(auto_now_add=True)
    promotions = models.ManyToManyField(Promotion, blank=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='product')
    is_digital = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title

    @property
    def new_price(self):
        now = timezone.now()
        if self.promotions.exists():
            if (
                product_promotion := self.promotions.filter(
                    start_date__lte=now, end_date__gte=now
                )
                .order_by('-discount')
                .first()
            ):
                return self.price * Decimal(1 - product_promotion.discount)

        if self.collection and self.collection.promotion:
            collection_promotion = self.collection.promotion
            if collection_promotion.start_date <= now and collection_promotion.end_date >= now:
                return self.price * Decimal(1 - collection_promotion.discount)

        return self.price

    class Meta:
        ordering = ['title', 'price']
        indexes = [
            models.Index(fields=['title', 'slug']),
            models.Index(fields=['price', 'title'])
        ]


class Stock(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.PROTECT, related_name='stock', primary_key=True)
    quantity_in_stock = models.PositiveIntegerField(
        validators=[MinValueValidator(1)])
    threshold = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self) -> str:
        return f'{self.product.title} - {self.quantity_in_stock}'

    class Meta:
        ordering = ['quantity_in_stock']
        indexes = [
            models.Index(fields=['quantity_in_stock', 'threshold']),
            models.Index(fields=['product', 'quantity_in_stock'])
        ]


class Review(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')

    rating_choices = [
        ('1', 'very bad'),
        ('1.5', 'bad'),
        ('2', 'not good'),
        ('2.5', 'below average'),
        ('3', 'average'),
        ('3.5', 'decent'),
        ('4', 'good'),
        ('4.5', 'very good'),
        ('5', 'excellent')
    ]

    rating = models.CharField(max_length=3, choices=rating_choices)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_updated = models.BooleanField(default=False)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.rating

    class Meta:
        ordering = ['created_at', 'is_updated', 'updated_at']
        indexes = [
            models.Index(fields=['product', 'customer', 'rating']),
        ]


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return 'Cart'


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='item')
    quantity = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return f'{self.product.title - {self.quantity}}'


class Order(models.Model):
    placed_at = models.DateTimeField(auto_now_add=True)

    status_fail = 'F'
    status_complete = 'C'
    status_pending = 'P'

    payment_status_choices = [
        (status_fail, 'Failed'),
        (status_complete, 'Complete'),
        (status_pending, 'Pending')
    ]

    status_delivered = 'D'
    status_shipped = 'S'

    order_status_choices = [
        (status_pending, 'Pending'),
        (status_shipped, 'Shipped'),
        (status_delivered, 'Delivered'),
        (status_complete, 'Picked Up')
    ]

    order_status = models.CharField(
        max_length=1, choices=order_status_choices, default=status_pending)

    payment_status = models.CharField(
        max_length=1, choices=payment_status_choices, default=status_pending)
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name='orders')

    def __str__(self) -> str:
        return f'{self.order_status} - {self.customer}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='item')
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='items')
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0.1)])
    quantity = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f'{self.product.title} - {self.quantity}'

    class Meta:
        ordering = ['quantity', 'unit_price']

        indexes = [
            models.Index(fields=['order', 'product']),
            models.Index(fields=['quantity', 'unit_price'])
        ]
