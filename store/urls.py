from django.urls import path, include
from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()

router.register('collections', views.CollectionViewSet, basename='collection')
router.register('promotions', views.PromotionViewSet, basename='promotions')
router.register('products', views.ProductViewSet, basename='product')
stock_router = routers.NestedDefaultRouter(
    router,
    'products',
    lookup='product'
)

review_router = routers.NestedDefaultRouter(
    router,
    'products',
    lookup='product'
)

review_router.register(
    'reviews',
    views.ReviewViewSet,
    basename='product-review'
)
stock_router.register('stock', views.StockViewSet, basename='product-stock')


router.register('carts', views.CartViewSet, basename='cart')
item_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
item_router.register('items', views.CartItemViewSet, basename='cart-item')
router.register('orders', views.OrderViewSet, basename='order')
urlpatterns = [
    path('', include(router.urls)),
    path('', include(stock_router.urls)),
    path('', include(review_router.urls)),
    path('', include(item_router.urls))
]
