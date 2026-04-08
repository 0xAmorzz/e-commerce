from django.urls import path

from .views import *

urlpatterns = [
    # categories
    path('categories/' , CategoryListCreateAPIView.as_view() , name='categories'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view() , name='categories-detail'),

    # products inside of a category
    path('categories/<int:pk>/products' , CategoryProductView.as_view() , 'category-products'),


    # brands
    path('brands/' , BrandListCreateAPIView.as_view(), name='brand'),
    path('brands/<int:pk>/' , BrandDetailView.as_view() , name='brand-detail'),
    path('brands/<int:pk>/products/' , BrandProductsView.as_view() , 'brand-products'),

    # attribute
    path('attributes/' , AttributeListCreateView.as_view() , name='attribute'),
    path('attributes/<int:pk>/' , AttributeDetailView.as_view(), name='attribute-detail'),

    # attribute-values
    path('attribute-values/' , AttributeValueListCreateView.as_view() , name='attribute-values'),
    path('attribute-values/<int:pk>/' , AttributeValueDetailView.as_view() , name='attribute-values-detail'),

    # products
    path('products/' , ProductListCreateView.as_view() , name='products'),
    path('products/<int:pk>/' , ProductDetailView.as_view() , name='products-detail'),
    path('products/<int:pk>/variants/', ProductVariantsView.as_view() , name='products-variants'),


    # variants
    path('variants/' , VariantListCreateView.as_view() , name='variants'),
    path('variants/<int:pk>/' , VariantDetailView.as_view() , name='variants-detail'),




]