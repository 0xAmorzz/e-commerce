from django.shortcuts import render
from rest_framework import generics , viewsets 
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (CategorySerializer , ProductSerializer , ProductBrandSerializer
                          , ProductAttributeSerializer , ProductAttributeValueSerializer)
from .models import (Category , Product , ProductBrand , ProductAttribute , ProductAttributeValue)

# Create your views here.

class CategoryGenderViewset(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    @action(detail=True , methods=['get'])
    # get all products inside of a category
    # /categories/{id}/products/
    def products(self , request , pk=None):
        category = self.get_object()
        qs = Product.objects.filter(category=category)
        serializer = ProductSerializer(qs , many=True , context={'request': request})
        return Response(serializer.data)
    

class ProductBrandViewSet(viewsets.ModelViewSet):
    queryset = ProductBrand.objects.all()
    serializer_class = ProductBrandSerializer
    @action(detail=True , methods=['get'])
    # /brands/{id}/products
    def products(self , request , pk=None):
        brand = self.get_object()
        qs = Product.objects.filter(brand=brand)
        serializer = ProductBrandSerializer(qs , many=True , context={'request':request})
        return Response(serializer.data)
    

# ATTRIBUTES VIEWS

class ProductAttributeViewSet(viewsets.ModelViewSet):
    # we are also fetching the values of the atrribute
    queryset = ProductAttribute.objects.prefetch_related('values')
    serializer_class = ProductAttributeSerializer


class ProductAttributeValueViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribute.objects.prefetch_related('attribute')
    serializer_class = ProductAttributeSerializer




    




