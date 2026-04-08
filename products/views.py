from django.shortcuts import render
from rest_framework import generics , viewsets 
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (CategorySerializer , ProductSerializer , ProductBrandSerializer
                          , ProductAttributeSerializer , ProductAttributeValueSerializer, ProductVariantSerializer)
from .models import (Category , Product , ProductBrand , ProductAttribute
                      , ProductAttributeValue , ProductVariant)

# Create your views here.

class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# for getting products inside a category
# /categories/{id}/products
class CategoryProductView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(category_id=self.kwargs['pk'])
    

class BrandListCreateAPIView(generics.ListCreateAPIView):
    queryset = ProductBrand.objects.all()
    serializer_class = ProductBrandSerializer


class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductBrand.objects.all()
    serializer_class = ProductBrandSerializer


# /brands/{id}/products
class BrandProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer()
    def get_queryset(self):
        return Product.objects.filter(brand_id=self.kwargs['pk'])



# ATTRIBUTES VIEWS

class AttributeListCreateView(generics.ListCreateAPIView):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer()


class AttributeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer()


class AttributeValueListCreateView(generics.ListCreateAPIView):
    queryset = ProductAttributeValue.objects.all()
    serializer_class = ProductAttributeValueSerializer()


class AttributeValueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductAttributeValue.objects.all()
    serializer_class = ProductAttributeValueSerializer()


# MAIN PRODUCT VIEWSET

class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    def get_queryset(self):
        Product.objects.select_related("brand" , "category").prefetch_related("attribute_vals",
                                                                              "variants__attribute_vals" , "variants__images")
        

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    def get_queryset(self):
        Product.objects.select_related("brand" , "category").prefetch_related("attribute_vals",
                                                                              "variants__attribute_vals" , "variants__images")
    


# /product/{id}/variants
class ProductVariantsView(generics.ListAPIView):
    serializer_class = ProductVariantSerializer
    def get_queryset(self):
        return ProductVariant.objects.filter(product_id = self.kwargs['pk'])
                                        



class VariantListCreateView(generics.ListCreateAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

class VariantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer





