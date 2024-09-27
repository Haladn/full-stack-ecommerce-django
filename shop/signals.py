from django.db.models.signals import post_save
from django.contrib.auth.models import User,Group 
from .models import Customer,Cart,CartItem
from django.core.cache import cache
from end_point.models import Laptop
from django.dispatch import receiver

#creating new customer
def customer_cart(sender,created,instance,**kwarges):
    if created:
        #create customer and cart for new user
        new_customer=Customer.objects.create(user=instance)
        new_cart=Cart.objects.create(customer=new_customer)
        
        #getting customer's cart in cache
        products_in_cache=cache.get('customer_cart')

        #adding products from cache to customer's cart
        if products_in_cache:
            for product in products_in_cache:
                id = product[0]
                quantity = product[1]

                #query laptop according to id
                laptop=Laptop.objects.get(id=id)
                CartItem.objects.create(
                    cart=new_cart,
                    laptop=laptop,
                    quantity=quantity,
                    price=laptop.price
                )
                
            cache.clear()

post_save.connect(customer_cart,sender=User)


# adding new user to its group
@receiver(post_save,sender=User)
def add_to_group(sender,created,instance,**kwargs):

    #getting or creating groups accordingly
    admin_group,_=Group.objects.get_or_create(name='admin')
    customer_group,_=Group.objects.get_or_create(name='customer')
    #checking if new user created
    if created:

        if instance.is_superuser:
            #adding superuser to admin group
            instance.groups.add(admin_group,customer_group)
        else:
             #adding other users to customer group
             instance.groups.add(customer_group)
        