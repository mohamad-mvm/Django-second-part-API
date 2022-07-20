from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet,basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewset,basename='carts')
router.register('customer', views.CustomerViewSet,basename='customer')
router.register('orders', views.OrderViewSet,basename='orders')

product_router=routers.NestedDefaultRouter(router,'products',lookup='product')
product_router.register('reviews',views.ReviewViewset,basename='product-reviews')

cart_router=routers.NestedDefaultRouter(router,'carts',lookup='cart')
cart_router.register('items',views.CartItemViewset,basename='cart-items')



# urlpatterns = router.urls + product_router.urls+cart_router.urls

# URLConf
urlpatterns =[
    path('',include(router.urls)),
    path('',include(product_router.urls)),
    path('',include(cart_router.urls))
] 