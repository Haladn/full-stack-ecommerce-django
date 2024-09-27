from .filters import LapotopFilter
from .models import Cart,Customer,CartItem
from django.contrib.auth.models import User
from django.core.cache import cache
from end_point.models import Laptop

def navbar(request):

    products=Laptop.objects.all()
    filtered_products= LapotopFilter(request.GET,queryset=products)  

    number_of_product=0
    if request.user.is_authenticated:
        customer,_=Customer.objects.get_or_create(user=request.user)
        cart,_=Cart.objects.get_or_create(customer=customer)
        all_itemes= cart.cartitem_set.all()
        for item in all_itemes:
            number_of_product+=item.quantity
    else:
        unauth_user_cart=cache.get('customer_cart',[])
        for product in unauth_user_cart:
            number_of_product+=product[1]
    context={

        'number_of_product':number_of_product,
        'filtered_products':filtered_products,
    }
    return context