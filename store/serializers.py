import collections
from decimal import Decimal
from rest_framework import serializers

from store.models import Product, Collection


class CollectionSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    title=serializers.CharField(max_length=255)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price','price_with_tax','collection']

    collection = CollectionSerializer ()
    price = serializers.DecimalField(        
                    max_digits=6,
                    decimal_places=2,
                    source='unit_price')
    price_with_tax=serializers.SerializerMethodField(method_name='get_price_with_tax')

    def get_price_with_tax(self, product:Product):
      return product.unit_price * Decimal(1.23)



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

