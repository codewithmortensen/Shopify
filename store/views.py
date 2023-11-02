from django.db.models.aggregates import Count
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, SAFE_METHODS, IsAuthenticated
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
        if self.request.method == SAFE_METHODS:
            return [AllowAny()]
        return [permissions.ShopifyModelPermission()]


class PromotionViewSet(ModelViewSet):
    queryset = models.Promotion.objects.all()
    serializer_class = serializers.PromotionSerializer

    permission_classes = [permissions.DjangoModelPermissions]


class ProductViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'head', 'options', 'delete']
    queryset = models.Product.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return serializers.CreateProductSerializer
        return serializers.ProductSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [permissions.ShopifyModelPermission()]

    def destroy(self, request, *args, **kwargs):
        if models.OrderItem.objects.filter(product_id=self.kwargs['pk']).count() > 0:
            return Response({'error': 'this Product con not be deleted'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class StockViewSet(ModelViewSet):
    def get_queryset(self):
        return models.Stock.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_class(self):
        methods = ['POST', 'PUT', 'PATCH']
        if self.request.method in methods:
            return serializers.CreateStockSerializer
        return serializers.StockSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [permissions.ShopifyModelPermission()]


class ReviewViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'head', 'options', 'delete']

    def get_queryset(self):
        return models.Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateReviewSerializer
        if self.request.method == 'PATCH':
            return serializers.UpdateReviewSerializer
        return serializers.ReviewSerializer

    def get_serializer_context(self):
        user_id = self.request.user.id
        return {
            'user_id': user_id,
            'product_id': self.kwargs['product_pk']
        }

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        if self.request.method == 'PATCH':
            return [permissions.IsReviewOwner()]
        if self.request.method == 'DELETE':
            return [permissions.ShopifyModelPermission()]
        return [AllowAny()]
