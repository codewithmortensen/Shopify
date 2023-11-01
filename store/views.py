from django.db.models.aggregates import Count
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from . import models, serializers, permissions


class CollectionViewSet(ModelViewSet):
    queryset = models.Collection.objects.all().annotate(
        products_count=Count('product')
    )

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH', 'PUT']:
            return serializers.CreateCollectionSerializer
        return serializers.CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        if models.Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error': 'this collection can not be deleted'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [permissions.ShopifyModelPermission()]


class PromotionViewSet(ModelViewSet):
    queryset = models.Promotion.objects.all()
    serializer_class = serializers.PromotionSerializer

    permission_classes = [permissions.DjangoModelPermissions]
