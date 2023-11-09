from django.db.models.aggregates import Count
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, SAFE_METHODS, IsAuthenticated
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from . import models, serializers, permissions, filters


class CustomerViewSet(ModelViewSet):
    http_method_names = ['get', 'patch', 'head', 'options']
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        'customer__id',
        'customer__first_name',
        'customer__last_name'
    ]

    ordering_fields = [
        'membership', 'birth_date',
        'customer__email', 'customer__first_name', 'customer__last_name'
    ]

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            return models.Customer.objects.select_related('customer').filter(customer_id=user.id).annotate(
                order_count=Count('orders')
            )

        return models.Customer.objects.select_related('customer').all().annotate(
            order_count=Count('orders')
        )

    def get_serializer_class(self):
        if self.request.method == 'PATCH' and self.request.user.is_staff:
            return serializers.AdminUpdateCustomerSerializer

        if self.request.method == 'PATCH':
            return serializers.UpdateCustomerSerializer

        return serializers.CustomerSerializer


class CollectionViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'slug']
    ordering_fields = ['title', 'products_count']
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
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [permissions.ShopifyModelPermission()]


class PromotionViewSet(ModelViewSet):
    queryset = models.Promotion.objects.all()
    serializer_class = serializers.PromotionSerializer

    permission_classes = [permissions.DjangoModelPermissions]


class ProductViewSet(ModelViewSet):

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'slug', 'collection__title']
    filterset_class = filters.ProductFilter
    ordering_fields = [
        'title', 'price',
        'stock__quantity_in_stock', 'last_update'
    ]
    http_method_names = ['get', 'post', 'patch', 'head', 'options', 'delete']
    queryset = models.Product.objects.select_related('collection__promotion') \
        .prefetch_related('promotions').select_related('stock').all().annotate(
        num_reviews=Count('reviews'),
    )

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
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = [
        'rating', 'created_at', 'is_updated', 'updated_at',
        'customer__customer__first_name', 'customer__customer__last_name']
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
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        if self.request.method == 'PATCH':
            return [permissions.IsReviewOwner()]

        return [permissions.ShopifyModelPermission()]


class CartViewSet(GenericViewSet, CreateModelMixin, RetrieveModelMixin):
    queryset = models.Cart.objects.all()
    serializer_class = serializers.CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'head', 'options', 'delete']

    def get_queryset(self):
        return models.CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateCartItemSerializer
        if self.request.method == 'PATCH':
            return serializers.UpdateCartItemSerializer
        return serializers.CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}


class OrderViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['order_status', 'payment_status', 'placed_at']
    search_fields = [
        'customer__customer__first_name',
        'customer__customer__last_name'
    ]
    http_method_names = ['get', 'patch', 'post', 'head', 'options']

    def get_queryset(self):
        if not self.request.user.is_staff:
            return models.Order.objects\
                .select_related('customer__customer')\
                .prefetch_related('item__product__promotions')\
                .prefetch_related('item__product__collection')\
                .filter(customer_id=self.request.user.id)
        return models.Order.objects\
            .select_related('customer__customer')\
            .prefetch_related('item__product__promotions')\
            .prefetch_related('item__product__collection')\
            .all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateOrderSerializer
        if self.request.method == 'PATCH':
            return serializers.UpdateOrderSerializer
        return serializers.OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = serializers.CreateOrderSerializer(
            data=self.request.data,
            context={'user_id': self.request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data)

    def get_permissions(self):
        if self.request.method in ['GET', 'POST', 'HEAD', 'OPTIONS']:
            return [IsAuthenticated()]
        return [permissions.ShopifyModelPermission()]
