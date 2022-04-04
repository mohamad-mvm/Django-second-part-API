from sqlite3 import connect
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models.aggregates import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework import status

from .models import Product, Collection,OrderItem,Reviews
from .serializers import ProductSerializer,CollectionSerializer,ReviewSerializer


# mearge 2 products class in one view set
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {'requesr': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product can not be deleted because it is assosiate with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):
    queryset=Collection.objects.annotate(product_count=Count('product')).all().order_by('id')
    serializer_class=CollectionSerializer

    def get_serializer_context(self):
        return {'requesr': self.request}

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Collection can not be deleted because it is assosiate with a product'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

class ReviewViewset(ModelViewSet):
    serializer_class=ReviewSerializer

    def get_queryset(self):
        return Reviews.objects.filter(product_id=self.kwargs['product_pk']).all()

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}



