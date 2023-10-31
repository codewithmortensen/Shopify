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
