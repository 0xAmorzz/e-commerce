from rest_framework import serializers
from .models import (ProductGender , Category , ProductAtrribute ,
                      ProductAtrributeValue , ProductBrand)

class ProductGenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGender
        fields = ('id' , 'name')


# main category serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id' , 'name' , 'image' , 'gender')


# a minimal category serializer for showcasing important fields (used in product serializers)
class CategoryMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id' , 'name')
