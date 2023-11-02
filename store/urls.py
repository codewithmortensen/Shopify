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


stock_router.register('stock', views.StockViewSet, basename='product-stock')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(stock_router.urls))
]
