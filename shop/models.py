from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from end_point.models import Laptop


class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE, blank=True,null=True)

    # username=models.CharField(max_length=100,null=True)
    # first_name=models.CharField(max_length=50,null=True,blank=True)
    # last_name=models.CharField(max_length=50,null=True,blank=True)

    profile_pic=models.ImageField(upload_to='images/', default='img.png',null=True,blank=True)
    phone=models.CharField(max_length=11,null=True,blank=True)  
    date_created=models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"customer: {self.id}"
     

class Cart(models.Model):
    customer=models.OneToOneField(Customer, on_delete=models.CASCADE, null=True)
    date_ctreated=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer.user.username

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    laptop=models.ForeignKey(Laptop,on_delete=models.CASCADE,null=True)
    quantity=models.PositiveSmallIntegerField(default=0)
    price=models.FloatField(default=00.00)
    date_created=models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        if self.cart:
            return f"{self.cart.customer.user.username}: {self.laptop.description[:25]}" 
        else:
            return "there's no item in the cart"   

    
class Address(models.Model):
    COUNTRIES=(
        ('UK','United Kingdom'),
        ('US','United States'),
        ('FR','France'),
        ('GER','Germany')
        )
    
    customer=models.OneToOneField(Customer,on_delete=models.CASCADE)

    first_name=models.CharField(max_length=200,null=True,)
    last_name=models.CharField(max_length=200,null=True)
    country=models.CharField(max_length=300,choices=COUNTRIES,blank=True)
    phone_number=models.CharField(max_length=50,blank=True)
    building_name=models.CharField(max_length=500,null=True,blank=True)
    addressline=models.CharField(max_length=500,null=True)
    city=models.CharField(max_length=300,null=True,)
    postal_code=models.CharField(max_length=300,null=True)
    formatted_address=models.CharField(max_length=500,null=True,blank=True) 
    date_created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.customer:
            return self.customer.user.username
        else:
            return f"No address"
    

class Order(models.Model):
    STATUS=(
        ('pendding','pendding'),
        ('on way to delivery','on way to delivery'),
        ('delivered','delivered')
    )
    customer=models.ForeignKey(Customer,null=True, on_delete=models.CASCADE)
    laptop=models.ForeignKey(Laptop,null=True,on_delete=models.CASCADE)
    total_price=models.FloatField(default=00.00)
    quantity=models.PositiveIntegerField(default=0)
    status=models.CharField(choices=STATUS, default='pendding',max_length=50)
    date_created=models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        if self.customer:
            return f"{self.customer.user.username}: {self.laptop.model}"
        else:
            return 'No Order'


    