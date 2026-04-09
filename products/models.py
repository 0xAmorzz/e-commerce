from django.db import models


# Create your models here.


# specify the genders for each product (ex: Men , Women , Kids)
class ProductGender(models.Model):
    name = models.CharField(max_length=10)



# holds the categories for the products (ex: Suit , Shirt , Coat , Shoes)
# there could be duplicates since a category for both men and women have different images
class Category(models.Model):
    name = models.TextField()
    image = models.ImageField(upload_to='products/categories/images' , null=True , blank=True)
    gender = models.ForeignKey(ProductGender , on_delete=models.CASCADE , related_name='categories')




class ProductAttribute(models.Model):
    name=models.CharField(max_length=50)
    def __str__(self):
        return f"{self.name}"




# an atrribute -> many attribute values(fk)
class ProductAttributeValue(models.Model): 
    attribute = models.ForeignKey(ProductAttribute , on_delete=models.CASCADE , related_name='values')
    value = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"



# for each brand there are multiple products of that brand
# brand -> many products(fk)
class ProductBrand(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    logo = models.ImageField(upload_to='brands/' , null=True , blank=True)


# category -> many products(fk) 
class Product(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category , on_delete=models.CASCADE , related_name='products')
    description = models.TextField(blank=True)
    brand = models.ForeignKey(ProductBrand , null=True , on_delete=models.SET_NULL)
    attribute_vals = models.ManyToManyField(ProductAttributeValue , blank=True , related_name='products')



# since a product could have many atrributes , and an attribute could be used
# in multiple products so its a ManyToMany rel defined below
class ProductVariant(models.Model):
    product = models.ForeignKey(Product , on_delete=models.CASCADE , related_name='variants')
    original_price = models.DecimalField(max_digits=8 , decimal_places=2)
    sale_price = models.DecimalField(max_digits= 8 , decimal_places=2 , null=True , blank=True)
    stock = models.IntegerField(default=0)
    attribute_vals = models.ManyToManyField(ProductAttributeValue ,  blank=True, related_name='variants')





# for each product item there are variations with sizes
# since for each product there could be multiple images ,
# thus we create a table for them
# product_item -> many images(fk)
class ProductImage(models.Model):
    image = models.ImageField(upload_to='products/images' , null=True , blank=True)
    variant = models.ForeignKey(ProductVariant , on_delete=models.CASCADE , related_name='images')


