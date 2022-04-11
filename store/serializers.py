# sourcery skip: avoid-builtin-shadow
import collections
from decimal import Decimal
from rest_framework import serializers

from store.models import Cart, Product, Collection, Reviews


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

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity']


# sourcery skip: avoid-builtin-shadow
class CartSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True)
    class Meta:
        model = Cart
        fields = ['id','items']