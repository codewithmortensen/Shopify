from rest_framework import serializers
from django.utils import timezone
from . import models


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id', 'title', 'price', 'new_price']


class CollectionSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField()
    featured_product = SimpleProductSerializer()
    products_count = serializers.IntegerField()

    class Meta:
        model = models.Collection
        fields = ['id', 'title', 'slug', 'featured_product',
                  'promotion', 'products_count']


class CreateCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ['title', 'featured_product', 'promotion']


class PromotionSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = models.Promotion
        fields = [
            'id', 'title', 'slug',  'description',
            'discount', 'start_date', 'end_date',
        ]
    now = timezone.now()

    def create(self, validated_data):

        start_date = validated_data['start_date']
        end_date = validated_data['end_date']

        errors = {}

        if start_date < self.now:
            errors['start_date'] = 'Start date cannot be in the past.'

        if end_date < self.now:
            errors['end_date'] = 'End date cannot be in the past.'

        if errors:
            raise serializers.ValidationError(errors)

        return super().create(validated_data)

    def update(self, instance: models.Promotion, validated_data):

        errors = {}

        if instance.start_date < self.now:
            errors['start_date'] = 'Start date cannot be in the past.'

        if instance.end_date < self.now:
            errors['end_date'] = 'End date cannot be in the past.'

        if errors:
            raise serializers.ValidationError(errors)

        return super().update(instance, validated_data)


class SimpleCollection(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ['id', 'title']


class SimplePromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Promotion
        fields = ['id', 'title', 'discount']


class ProductSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField()
    collection = SimpleCollection()
    promotions = SimplePromotionSerializer(many=True)

    class Meta:
        model = models.Product
        fields = [
            'id', 'title', 'slug',  'description',
            'price', 'new_price', 'last_update',
            'collection', 'promotions', 'status', 'last_update'
        ]

    status = serializers.SerializerMethodField(method_name='get_status')

    def get_status(self, product: models.Product):
        if not hasattr(product, 'stock') or product.stock.quantity_in_stock == 0:
            return 'Out of Stock'
        return 'In Stock'


class CreateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['title', 'price', 'description', 'collection', 'promotions']


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stock
        fields = ['product_id', 'quantity_in_stock', 'threshold']


class CreateStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stock
        fields = ['quantity_in_stock', 'threshold']

    def save(self, **kwargs):
        product_id = self.context['product_id']
        quantity = self.validated_data['quantity_in_stock']
        threshold = self.validated_data['threshold']
        try:
            stock = models.Stock.objects.get(product_id=product_id)
            stock.quantity_in_stock = quantity
            stock.threshold = threshold
            stock.save()
            self.instance = stock
        except models.Stock.DoesNotExist:
            self.instance = models.Stock.objects.create(
                product_id=product_id, **self.validated_data)
        return self.instance


class SimpleCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['customer_id', 'first_name', 'last_name', 'membership']


class ReviewSerializer(serializers.ModelSerializer):
    customer = SimpleCustomerSerializer()

    class Meta:
        model = models.Review
        fields = [
            'id', 'customer', 'rating',
            'description', 'created_at', 'is_updated', 'updated_at'
        ]


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ['rating', 'description']

    def create(self, validated_data):
        user_id = self.context['user_id']
        product_id = self.context['product_id']
        return models.Review.objects.create(customer_id=user_id, product_id=product_id, **validated_data)


class UpdateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ['rating', 'description']

    def update(self, instance: models.Review, validated_data):
        instance.is_updated = True
        instance.updated_at = timezone.now()
        instance.rating = validated_data.get('rating', instance.rating)
        instance.description = validated_data.get(
            'description', instance.description)

        return super().update(instance, validated_data)
