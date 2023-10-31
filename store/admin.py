from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.db.models.aggregates import Count
from django.utils.http import urlencode
from django.utils.html import format_html
from django.db.models import F

from . import models


class AddressInline(admin.TabularInline):
    model = models.Address
    extra = 0


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']
    list_display = [
        'customer_id', 'first_name', 'last_name',
        'email', 'membership', 'order_count'
    ]
    list_filter = ['membership']
    list_editable = ['membership']
    inlines = [AddressInline]
    list_per_page = 10

    @admin.display(ordering='order_count')
    def order_count(self, customer: models.Customer):
        url = reverse('admin:store_order_changelist') + '?' + urlencode({
            'customer_id': str(customer.id)
        })
        return format_html('<a href={}>{}</a>', url, customer.order_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            order_count=Count('orders')
        )


@admin.register(models.Promotion)
class PromotionAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['title']
    }
    search_fields = ['title__istartswith']
    list_display = ['id', 'title', 'discount', 'start_date', 'end_date']
    list_per_page = 10


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['title']
    }
    autocomplete_fields = ['promotion', 'featured_product']
    search_fields = ['title__istartswith']
    list_display = ['id', 'title', 'featured_product',
                    'products_count', ]
    list_per_page = 10

    def products_count(self, collection: models.Collection):
        url = reverse('admin:store_product_changelist') + '?' + urlencode({
            'collection_id': str(collection.id)
        })

        return format_html('<a href={}>{}</a>', url, collection.products_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory status'
    parameter_name = 'inventory status'

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            ('low', 'low'),
            ('ok', 'ok')
        ]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == 'low':
            return queryset.filter(stock__quantity_in_stock__lte=F('stock__threshold'))
        if self.value() == 'ok':
            return queryset.filter(stock__quantity_in_stock__gt=F('stock__threshold'))


class StockAdminInline(admin.TabularInline):
    model = models.Stock
    min_num = 1
    extra = 0


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title__istartswith', 'id']
    autocomplete_fields = ['collection']
    inlines = [StockAdminInline]
    prepopulated_fields = {
        'slug': ['title']
    }
    list_display = [
        'id', 'title', 'price',
        'collection', 'inventory_status', 'is_digital', 'new_price'
    ]
    list_filter = ['collection', 'is_digital', 'last_update', InventoryFilter]
    list_per_page = 10

    @admin.display(ordering='stock__quantity_in_stock')
    def inventory_status(self, product: models.Product):
        if product.stock.quantity_in_stock > product.stock.threshold:
            return 'Ok'
        return 'Low'


@admin.register(models.Review)
class ReviewsAdmin(admin.ModelAdmin):
    search_fields = [
        'customer__first_name__istartswith',
        'customer__last_name__istartswith',
        'product__title__istartswith'
    ]
    autocomplete_fields = ['customer', 'product']
    list_display = ['id', 'customer', 'product', 'rating', 'is_updated']
    list_filter = ['rating', 'created_at', 'updated_at', 'is_updated']
    list_per_page = 10


@admin.register(models.Stock)
class StockAdmin(admin.ModelAdmin):
    autocomplete_fields = ['product']
    search_fields = ['product__title__istartswith']
    actions = ['clear_inventory']
    list_display = [
        'product_id', 'product', 'quantity_in_stock',
        'inventory_status'
    ]
    list_per_page = 10

    @admin.display(ordering='inventory_status')
    def inventory_status(self, stock: models.Stock):
        if stock.quantity_in_stock > stock.threshold:
            return 'Ok'
        return 'low'

    @admin.action(description='clear stock')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(quantity_in_stock=0)
        message = f'you have successfully updated {
            updated_count} product stock '
        self.message_user(request, message)


class OrderItemAdminInline(admin.TabularInline):
    autocomplete_fields = ['product']
    model = models.OrderItem
    min_num = 1
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        'customer__first_name__istartswith',
        'customer__first_name__istartswith'
    ]
    list_display = ['id', 'customer', 'order_status', 'payment_status']
    list_editable = ['order_status', 'payment_status']
    list_filter = ['payment_status', 'order_status', 'placed_at']
    autocomplete_fields = ['customer']
    actions = ['payment_complete']
    inlines = [OrderItemAdminInline]

    @admin.action(description='payment completed')
    def payment_complete(self, request, queryset: QuerySet):
        updated_count = queryset.update(payment_status='C')
        placeholder = 'orders' if updated_count > 1 else 'order'
        message = f'you have successfully mark {
            updated_count} {placeholder} as complete'
        self.message_user(request, message)
