from django.shortcuts import render
from rest_framework import generics , viewsets 
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (CategorySerializer , ProductSerializer)
from .models import (Category , Product)

# Create your views here.

class CategoryGenderViewset(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    @action(detail=True , methods=['get'])
    # /categories/{id}/products/
    def products(self , request , pk=None):
        category = self.get_object()
        qs = Product.objects.filter(category=category)
        serializer = ProductSerializer(qs , many=True , context={'request': request})
        return Response(serializer.data)



