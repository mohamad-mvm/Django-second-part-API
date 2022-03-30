from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('product_list/', views.product_list),
    path('product_list/<int:id>', views.product_detail),
    path('collection/', views.collection_list),
    path('collection/<int:id>', views.collection_detail),
]
