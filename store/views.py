from sqlite3 import connect
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.pagination import PageNumberPagination
from .pagination import DefaultPagination
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser,DjangoModelPermissions,DjangoModelPermissionsOrAnonReadOnly
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet,GenericViewSet
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework import status
from .permission import IsAdminOrReadOnly,FullDjangoModelPermissions, ViewCustomerHistory

from .models import CartItem, Customer, Order, Product, Collection,OrderItem,Reviews,Cart
from .serializers import CreateOrderSerialiser, CustomerSerializer, ProductSerializer,CollectionSerializer,ReviewSerializer,CartSerializer,CartItemSerializer,AddToCartSerializer,UpdateCartItemSerializer, OrderSerializer, UpdateOrderSerializer
from.filters import ProductFilter


# mearge 2 products class in one view set
class ProductViewSet(ModelViewSet):
    queryset=Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends=[DjangoFilterBackend, SearchFilter,OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes=[IsAdminOrReadOnly]
    search_fields = ['title', 'description', 'collection__title']
    ordering_fields = ['unit_price', 'last_update']

    def get_serializer_context(self):
        return {'request': self.request}

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

class CartViewset(CreateModelMixin,
                    RetrieveModelMixin,
                    DestroyModelMixin,
                    GenericViewSet,):
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related('items__product').all()


class CartItemViewset(ModelViewSet):
    http_method_names = ['post', 'patch', 'get', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddToCartSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer 

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id=self.kwargs['cart_pk']).all()

class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

    # def get_permissions(self):
    #     return [AllowAny()] if self.request.method == 'GET' else [IsAuthenticated()]

    @action(detail=True,permission_classes=[ViewCustomerHistory])
    def history(self, request,pk):
        return Response('ok')

    @action(detail=False,methods=['GET','PUT'],permission_classes=[IsAuthenticated])
    def me(self, request):
        (customer,created) = Customer.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



class OrderViewSet(ModelViewSet):
    http_method_names = ['get','patch','delete','head','options']

    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return[IsAdminUser()]
        return[IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerialiser(data=request.data, context= {'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer=OrderSerializer(order)

        return Response(serializer.data)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method=='POST':
            return CreateOrderSerialiser
        if self.request.method=="PATCH":
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user=self.request.user
        if user.is_staff:
            return Order.objects.all()
        (customer_id,CREATED)=Customer.objects.only('id').get_or_create(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id).all()
