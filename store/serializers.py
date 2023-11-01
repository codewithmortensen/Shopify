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
