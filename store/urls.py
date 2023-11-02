from django.urls import path, include
from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()

router.register('collections', views.CollectionViewSet, basename='collection')
router.register('promotions', views.PromotionViewSet, basename='promotions')
router.register('products', views.ProductViewSet, basename='product')
urlpatterns = [
    path('', include(router.urls))
]
