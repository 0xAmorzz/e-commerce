from rest_framework import serializers
from .models import ( Product , ProductGender , Category , ProductAtrribute ,
                      ProductAtrributeValue , ProductVariant , ProductBrand, ProductImage)


# ------------------------------- CATEGORY SERIALIZERS --------------------------

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


# ------------------------------- PRODUCT SERIALIZERS --------------------------
class ProductGenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGender
        fields = ('id' , 'name')

class ProductBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrand
        fields = ('id' , 'name' , 'description' , 'logo')


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='atrribute.name' , read_only=True)
    class Meta:
        model = ProductAtrributeValue
        fields = ('id' , 'attribute' , 'attribute_name' , 'value')


class ProductAttributeSerializer(serializers.ModelSerializer):
    values = ProductAttributeValueSerializer(many=True , read_only=True)
    class Meta:
        model = ProductAtrribute
        fields = ('id' , 'name' , 'values')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id' , 'image')


# MAIN PRODUCT SERIALIZER
class ProductVariantSerializer(serializers.ModelSerializer):
    attribute_vals = ProductAttributeValueSerializer(many=True , read_only=True)
    images = ProductImageSerializer(many=True , read_only=True)

    class Meta:
        model = ProductVariant
        fields = ('id' , 'original_price' , 'sale_price' , 'stock' ,
                   'attribute_vals' , 'images')
        
    

class ProductSerializer(serializers.ModelSerializer):
    brand = ProductBrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    atrribute_vals = ProductAttributeValueSerializer(many=True , read_only=True)
    variants = ProductVariantSerializer(many=True , read_only=True)

    class Meta:
        model = Product
        fields = ('id' , 'name' , 'description' ,
                   'brand' , 'category' , 'attribute_vals', 'variants')


    
