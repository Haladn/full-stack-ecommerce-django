from django.db import models
from django.contrib.auth.models import User


class Laptop(models.Model):
    # related_name is for reverse relationship  like  (User.laptop) but without related_name we have to use (User.laptop_set.all())
    owner=models.ForeignKey(User,on_delete=models.CASCADE, related_name='laptop',null=True,blank=True)

    description=models.TextField(max_length=500,null=True)
    price=models.FloatField(default=00.00)
    image=models.ImageField(max_length=500,null=True)
    # href=models.CharField(max_length=1000,null=True)
    resolution=models.CharField(max_length=500,null=True,blank=True)
    color=models.CharField(max_length=500,null=True,blank=True)
    system=models.CharField(max_length=500,null=True,blank=True)
    cpu=models.CharField(max_length=500,null=True,blank=True)
    model=models.CharField(max_length=500,null=True,blank=True)
    weight=models.CharField(max_length=150,null=True,blank=True)

    quantity=models.PositiveIntegerField(default=0)
    category=models.CharField(max_length=100 ,default='Gaming Laptop')
    date_created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.model
    

    