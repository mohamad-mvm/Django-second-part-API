from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('product_list/', views.ProductList.as_view()),
    path('product_list/<int:id>', views.ProductDetail.as_view()),
    path('collection/', views.collection_list),
    path('collection/<int:id>', views.collection_detail),
]
