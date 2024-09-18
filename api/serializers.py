from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['pid', 'title', 'price', 'stock_count', 'in_stock', 'description']  # Fields to return
