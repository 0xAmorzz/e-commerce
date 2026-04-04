from django.db import models


# Create your models here.


# specify the genders for each product (ex: Men , Women , Kids)
class ProductGender(models.Model):
    name = models.TextField(max_length=10)



# holds the categories for the products (ex: Suit , Shirt , Coat , Shoes)
# there could be duplicates since a category for both men and women have different images
class Category(models.Model):
    name = models.TextField()
    image = models.ImageField(upload_to='/products/categories/images' , null=True , blank=True)
    gender = models.ForeignKey(ProductGender , on_delete=models.CASCADE , related_name='categories')



# category -> many products(fk) 
class Product(models.Model):
    name = models.CharField()
    category = models.ForeignKey(Category , on_delete=models.CASCADE , related_name='products')
    description = models.CharField()




# for each color there is multiple products (ex-> blue: (coat , shoe , shirt))
# so color -> many product items(fk)
class ProductColor(models.Model):
    color = models.CharField(max_length=50)



# for each size there is multiple products (ex-> L: (shoe , shirt , pants))
# so size -> many product items(fk)
class ProductSize(models.Model):
    name = models.CharField(max_length=100)



# for each product there are variants with different colors , prices
class ProductItem(models.Model):
    product = models.ForeignKey(Product , on_delete=models.CASCADE , related_name='items')
    color = models.ForeignKey(ProductColor , on_delete=models.SET_NULL , related_name='colors')
    size = models.ForeignKey(ProductSize , on_delete=models.CASCADE , related_name='sizes')
    original_price = models.DecimalField(max_digits=8 , decimal_places=2)
    sale_price = models.DecimalField(max_digits= 8 , decimal_places=2 , null=True , blank=True)
    stock = models.IntegerField()





# since for each product there could be multiple images ,
# thus we create a table for them
# product -> many images(fk)
class ProductImage(models.Model):
    image = models.ImageField(upload_to='/products/images' , null=True , blank=True)
    product = models.ForeignKey(ProductItem , on_delete=models.CASCADE , related_name='images')


