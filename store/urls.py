from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('product_list/', views.ProductList.as_view()),
    path('product_list/<int:pk>', views.ProductDetail.as_view()),
    path('collection/', views.collection_list.as_view()),
    path('collection/<int:pk>', views.collection_detail.as_view()),
]
