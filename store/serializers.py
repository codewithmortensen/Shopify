from rest_framework import serializers
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
