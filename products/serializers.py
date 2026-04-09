from rest_framework import serializers
from .models import ( Product , ProductGender , Category , ProductAttribute ,
                      ProductAttributeValue , ProductVariant , ProductBrand, ProductImage)


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
    attribute_name = serializers.CharField(source='attribute.name' , read_only=True)
    class Meta:
        model = ProductAttributeValue
        fields = ('id' , 'attribute' , 'attribute_name' , 'value')


class ProductAttributeSerializer(serializers.ModelSerializer):
    values = ProductAttributeValueSerializer(many=True , read_only=True)
    class Meta:
        model = ProductAttribute
        fields = ('id' , 'name' , 'values')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id' , 'image')


# MAIN PRODUCT SERIALIZER
class ProductVariantSerializer(serializers.ModelSerializer):
    attribute_vals = ProductAttributeValueSerializer(many=True , read_only=True)
    attribute_val_ids = serializers.PrimaryKeyRelatedField(
        queryset=ProductAttributeValue.objects.all(),
        many=True,
        write_only=True,
        source='attribute_vals',
        required=False,
    )
    images = ProductImageSerializer(many=True , read_only=True)

    class Meta:
        model = ProductVariant
        fields = ('id' , 'original_price' , 'sale_price' , 'stock' ,
                   'attribute_vals' , 'attribute_val_ids' , 'images')
        
    

class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryMinimalSerializer(read_only=True)
    brand = ProductBrandSerializer(read_only=True)
    image = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True , read_only=True)

    class Meta:
        model = Product
        fields = [
            'id' , 'name' , 'category' , 'brand' , 'image' ,  'variants' 
        ]

    def get_image(self , obj):
        img = ProductImage.objects.filter(variant__product=obj).first()
        if img:
            return ProductImageSerializer(img , context=self.context).data
            
        return None
        


        

class ProductDetailSerializer(serializers.ModelSerializer):
    # the incoming fields are only for listing pages (not available for write)
    category = CategoryMinimalSerializer(read_only=True)
    brand = ProductBrandSerializer(read_only=True)
    attribute_vals = ProductAttributeValueSerializer(many=True , read_only=True)
    variants = ProductVariantSerializer(many=True , read_only=True)

    # write fields
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all() , write_only=True , source='category')
    brand_id = serializers.PrimaryKeyRelatedField(queryset=ProductBrand.objects.all() , write_only=True , source='brand')
    attribute_vals_ids = serializers.PrimaryKeyRelatedField(queryset=ProductAttributeValue.objects.all() , many=True , write_only=True ,
                                                             source='attribute_vals' , required=False)

    variants_data = ProductVariantSerializer(many=True , write_only=True , required=False)
    

    class Meta:
        model = Product
        fields = [
            'id' , 'name' , 'description' , 'category' , 'brand' , 'attribute_vals' , 'variants',
            'category_id' , 'brand_id' , 'attribute_vals_ids' , 'variants_data'
        ]

    def create(self, validated_data):
        attribute_vals = validated_data.pop('attribute_vals', [])
        variants_data  = validated_data.pop('variants_data', [])

        # create the product
        product = Product.objects.create(**validated_data)

        # assign product-level attribute values
        if attribute_vals:
            product.attribute_vals.set(attribute_vals)

        # create each variant
        for variant_data in variants_data:
            variant_attrs = variant_data.pop('attribute_vals', [])
            variant = ProductVariant.objects.create(product=product, **variant_data)
            if variant_attrs:
                variant.attribute_vals.set(variant_attrs)

        return product



    
