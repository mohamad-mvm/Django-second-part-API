from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_nested import routers

from store.models import Cart
from . import views

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet,basename='products')
router.register('collections', views.CollectionViewSet)
router.register('cart', views.CartViewset)

product_router=routers.NestedDefaultRouter(router,'products',lookup='product')
product_router.register('reviews',views.ReviewViewset,basename='product-reviews')



# URLConf
urlpatterns =[
    path('',include(router.urls)),
    path('',include(product_router.urls)),
] 