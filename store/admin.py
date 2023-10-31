from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.db.models.aggregates import Count
from django.utils.http import urlencode
from django.utils.html import format_html
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
