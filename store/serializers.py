# sourcery skip: avoid-builtin-shadow
from dataclasses import fields
from decimal import Decimal
from pyexpat import model
from django.db import transaction
from django.forms import ValidationError
from rest_framework import serializers
from .models import Cart, CartItem, Customer, Order, Product, Collection, Reviews, OrderItem


class CollectionSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    title=serializers.CharField(max_length=255)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description','slug','description', 'inventory',  'unit_price','price_with_tax','collection']

    # collection = CollectionSerializer ()
    # price = serializers.DecimalField(        
    #                 max_digits=6,
    #                 decimal_places=2,
    #                 source='unit_price')
    price_with_tax=serializers.SerializerMethodField(method_name='get_price_with_tax')

    def get_price_with_tax(self, product:Product):
      return product.unit_price * Decimal(1.23)

    # def create(self, validated_data):
    #     product = Product(**validated_data)
    #     product.inventory=1
    #     product.save()
    #     return product

    # def update(self, instance, validated_data):
    #     instance.inventory = validated_data.get('inventory')
    #     instance.save()
    #     return instance



# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(        
#                         max_digits=6,
#                         decimal_places=2,
#                         source='unit_price')
#     price_with_tax=serializers.SerializerMethodField(method_name='get_price_with_tax')
#     collections_set = CollectionSerializer (source='collection')

    # def get_price_with_tax(self, product:Product):
    #     return product.unit_price * Decimal(1.23)

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title','product_count']

    product_count = serializers.IntegerField(read_only=True)

    # def get_product_count(self, collection:Collection):
    #     return collection.product_set.count()

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        product_id=self.context['product_id']
        return Reviews.objects.create(product_id=product_id,**validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity','total_price']

    def get_total_price(self, cart_item:CartItem):
        return cart_item.product.unit_price * cart_item.quantity


# sourcery skip: avoid-builtin-shadow
class CartSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    class Meta:
        model = Cart
        fields = ['id','items', 'total_price']

    def get_total_price(self, cart:Cart):
        return sum(item.product.unit_price * item.quantity for item in cart.items.all())

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = [ 'quantity']

class AddToCartSerializer(serializers.ModelSerializer):
    product_id=serializers.IntegerField()

    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Product does not exist')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data.get('quantity')


        try:
            cart_item =CartItem.objects.get(cart_id=cart_id,product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # CartItem.objects.create(cart_id=cart_id,product_id=product_id,quantity=quantity)
            self.instance = CartItem.objects.create(cart_id=cart_id,**self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

class CustomerSerializer(serializers.ModelSerializer):

    user_id=serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'birth_date','membership','phone']




class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at','payment_status','items']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model= Order
        fields = ['payment_status']


class CreateOrderSerialiser(serializers.Serializer):
    cart_id=serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise(ValidationError('cart was not Exist.'))
        if not CartItem.objects.filter(cart_id=cart_id).exists():
            raise(ValidationError('This cart has not any Items'))
        return cart_id


    def save(self, **kwargs):
        with transaction.atomic():
            cart_id=self.validated_data['cart_id']

            customer=Customer.objects.get(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)
            cartItems = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            orderItems = [
                OrderItem(order=order,
                            product = item.product,
                            quantity = item.quantity,
                            unit_price = item.product.unit_price
                )
                for item in cartItems
            ]
            OrderItem.objects.bulk_create(orderItems)

            Cart.objects.filter(pk=cart_id).delete()
            return order




