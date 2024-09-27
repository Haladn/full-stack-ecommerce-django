
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.http import HttpResponse,JsonResponse
from .models import CartItem,Cart,Customer,Address,Order
from .filters import LapotopFilter
from .forms import Registerationform, LaptopForm, AddressForm,CustomerForm,CustomUserChangeForm,OrderForm
from django.contrib.auth import login,logout,authenticate
from django.core.cache import cache
from django.contrib import messages
from django.conf import settings
import requests,json
from urllib.parse import urlencode
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.views import View
from end_point.models import Laptop
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count,Sum,F
from django.contrib.auth.decorators import login_required
from .decorators import admin_only,htmx_request_only
from django.contrib.auth.models import User
import json

@admin_only
def admin_add_customer(request):

    if request.method== 'POST':
        form=Registerationform(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin')
        form.errors
    else:
        form=Registerationform()

    context={
        'form':form,
    }
    return render(request,'shop/add_customer.html',context)

@admin_only
def admin_update_customer(request,pk):

    customer=get_object_or_404(Customer,id=pk)
    user=customer.user
    
    if request.method=="POST":
        button=request.POST.get('button')
        if button == 'save':
            form=CustomUserChangeForm(request.POST,instance=user)
            form1=CustomerForm(request.POST,request.FILES ,instance=customer)
            if form.is_valid() and form1.is_valid():
                form.full_clean()
                form1.full_clean()
                form.save()
                form1.save()
                return redirect('admin')
            form.errors
            form1.errors

        elif button == 'delete':
            customer.user.delete()
            return redirect('admin')

    else:        
        form=CustomUserChangeForm(instance=user)
        form1=CustomerForm(instance=customer)
    context={
        "form":form,
        "form1":form1,
        'customer':customer,
    }
    return render(request,'shop/update_customer.html',context)
    


@admin_only
def admin_update_product(request,pk=None):
    #checking pk
    if pk:
        product=get_object_or_404(Laptop,id=pk)
    else:
        product=None

    # handling post request
    if request.method == 'POST':
        #getting button
        button=request.POST.get('button')
        
        #handling data accordingly
        if button == "save":
            form=LaptopForm(request.POST,request.FILES,instance=product)

            #checking form
            if form.is_valid():
                form.save()
                return redirect('admin')
            form.errors
        elif button == 'delete':
            #deleting the item 
            if product:
                product.delete()
            return redirect('admin')
    else:
        form=LaptopForm(instance=product)

    context={
        'form':form,
        'product':product,
    }
    return render(request,'shop/update_products.html',context)


@admin_only
def admin_update_orders(request,pk=None):
    #checking pk
    if pk:
        order=get_object_or_404(Order,id=pk)
    else:
        order=None

    if request.method == 'POST':
        button=request.POST.get('button')
        
        #handling data accordingly
        if button == 'save':
            form = OrderForm(request.POST, instance=order)

            #checking form
            if form.is_valid():
                form.save()
                return redirect('admin')
            form.errors
        elif button== 'delete':
            #deleting the item 
            if order:
                order.delete()
            return redirect('admin')
    else:
        form=OrderForm(instance=order)
    context={
        'form':form,
        'order':order,
    }
    return render(request,'shop/update_orders.html',context)

@admin_only
def admin_dashboard(request):

    #getting admin username
    admin=request.user.username

    #getting customers
    customers=Customer.objects.all()

    #getting orders
    orders = Order.objects.all()

    #getting Products
    products=Laptop.objects.all()

    context={
        'admin':admin,
        'customers':customers,
        'orders':orders,
        'products':products,

    }
    return render(request,'shop/admin.html',context)

@login_required(login_url='login')
def checkout(request,pk=None,quantity=None,sutotal=None):
    #getting customer data
    customer=Customer.objects.get(user=request.user)
    customer_cart=Cart.objects.get(customer=customer)
    address=Address.objects.get(customer=customer)

    #checking for a product or subtotal
    if pk and quantity:
        product=Laptop.objects.get(id=pk)

        # using get_or_create on method for escaping errors when a customer click
        # buy now from product_detail page and the product is not in customer's cart

        product_in_cart,created=CartItem.objects.get_or_create(cart=customer_cart,laptop=product)

        #adding price and quantity after creating and updating quantity in stock
        if created:
            product_in_cart.price=product.price
            product_in_cart.quantity=quantity
            product_in_cart.save()
            product.quantity -= quantity
            product.save()
        
        total_price=product_in_cart.price * product_in_cart.quantity
        context={
            'product':product_in_cart,
            'total_price':total_price,
            'address':address,
        }
    else:
        #reverse relation
        products_in_cart=customer_cart.cartitem_set.all()

        #getting total price and subtotal
        total_price=CartItem.objects.filter(cart=customer_cart).aggregate(total_price=Sum( F('price') * F('quantity')))
        subtotal = CartItem.objects.filter(cart=customer_cart).aggregate(subtotal=Sum('quantity'))
    
        context={
            'products':products_in_cart,
            'address':address,
            'total_price':total_price['total_price'],
            "subtotal":subtotal['subtotal'],
        }
        
    
    return render(request,'shop/checkout.html',context)

@login_required(login_url='login')
def paymentComplete(request,pk=None, quantity=None):
    #getting customer's cart
    customer = Customer.objects.get(user=request.user)
    customer_cart = Cart.objects.get(customer=customer)
    
    #checking pk and quantity
    if request.method == "POST":
        data=json.loads(request.body)
        total_price=data['total_price']
        if pk and quantity:
            #getting product in cart
            product = Laptop.objects.get(id=pk)
            product_in_cart = CartItem.objects.get(cart=customer_cart,laptop=product)
            

            #creating customer order
            customer_order = Order.objects.create(
                customer=customer,
                laptop=product,
                total_price=total_price,
                quantity=quantity
            )

            product_in_cart.delete()
            return JsonResponse({'message': 'Payment and order creation successful'})
            
        else:
            
            #getting subtotal from customer's cartitem
            products_in_cart=customer_cart.cartitem_set.all()

            #adding subtotal to ordered models
            for product in products_in_cart:
                customer_order=Order(
                    customer=customer,
                    laptop=product.laptop,
                    total_price=total_price,
                    quantity=product.quantity,
                )
                #saving instance
                customer_order.save()

            #deleting product from customer's cart
            products_in_cart.delete()

    return JsonResponse('payment was successfull',safe=False)


class CartView(View):
    template_name='shop/cart.html'
    http_method_names=['get','post']


    def get(self,request):

        if request.user.is_authenticated:
            customer=Customer.objects.get(user=request.user)
            customer_cart=Cart.objects.get(customer=customer)
            customer_products=customer_cart.cartitem_set.all()
            total_price=0
            subtotal=0
            for customer_product in customer_products:
                subtotal+=customer_product.quantity
                total_price += customer_product.laptop.price* customer_product.quantity
            context={
                'customer_products':customer_products,
                'subtotal':subtotal,
                'total_price':total_price,  
            }

            return render(request,self.template_name,context)
        
        else:
            unauth_user_cart=cache.get('customer_cart',[])
            subtotal=0
            total_price=0
            products_id=[]
            # product's id and quantity stored in a tuple, we unpack the tuple to processing the data
            for product in unauth_user_cart:
                products_id.append(product[0])
                subtotal += product[1]
                id=product[0]
                laptop = Laptop.objects.get(id=product[0])
                total_price += laptop.price * product[1]
            products=Laptop.objects.filter(id__in=products_id)
            all_products=zip(products,unauth_user_cart)
            context={
                'all_products':all_products,
                'unauth_user_cart':unauth_user_cart,
                'products':products,
                'subtotal':subtotal,
                'total_price':total_price,
            }
            return render(request,self.template_name,context)
    
    def post(self,request):
        button = request.POST.get('button')
        if request.user.is_authenticated:
            # getting customer's cart
            customer=Customer.objects.get(user=request.user)
            customer_cart=Cart.objects.get(customer=customer)

            #checking for customer's address
            address=Address.objects.filter(customer=customer)

            if button=='subtotal':
                if address:
                    return redirect('checkout')
                else:
                    subtotal=True
                    return redirect('address_subtotal',subtotal=subtotal)

            elif button=='remove':
                product_id=int(request.POST.get('product_id'))
                product_quantity=int(request.POST.get('product_quantity'))
                laptop=Laptop.objects.get(id=product_id)
                customer_product_in_cart=CartItem.objects.get(cart=customer_cart,laptop=laptop)

                #deleting product in customer's cartitem
                customer_product_in_cart.delete()
                laptop.quantity+=product_quantity
                laptop.save()
            elif button=='checkout':
                product_id=int(request.POST.get('product_id'))
                product_quantity=int(request.POST.get('product_quantity'))
                laptop=Laptop.objects.get(id=product_id)
                customer_product_in_cart=CartItem.objects.get(cart=customer_cart,laptop=laptop)

                if address:
                    return redirect('checkout_params',pk=product_id,quantity=product_quantity)
                else:
                    return redirect('address_params',pk=product_id,quantity=product_quantity)

            return redirect('cart')
    

        else:
            product_id=request.POST.get('product_id')
            product_quantity=request.POST.get('product_quantity')

            unauth_user_cart=cache.get('customer_cart') 
            print(unauth_user_cart)
            print("product_id: ",product_id)
            if button=='subtotal':
                return redirect('login')
            elif button=='remove':
                
                is_in_cart=False
                for product in unauth_user_cart:
                    if str(product[0]) == str(product_id):
                        unauth_user_cart.remove(product)
                        cache.set('customer_cart',unauth_user_cart)
                        
                        is_in_cart=True
                        break
                return redirect('cart')
                    
            elif button=='checkout':
                return redirect('login')

   
def address_validation(**kwargs):
    # getting keys from kwargs
    addressline=kwargs.get('addressline')
    locality=kwargs.get('locality')
    postal_code=kwargs.get('postal_code')
    country = kwargs.get('country')

    #getting google api key
    API_KEY=settings.GOOGLE_VALIDATION_KEY

    #google address validation api
    url = f"https://addressvalidation.googleapis.com/v1:validateAddress?key={API_KEY}"
    
    #request body
    body={
    "address": {
        "regionCode": f"{country}",
        "addressLines": [f"{addressline}", f"{locality}, {postal_code}"]
        },
    }

    response=requests.post(url,json=body)
    return response

@login_required(login_url='login')   
def address(request,pk=None,quantity=None,subtotal=None):
    customer=Customer.objects.get(user=request.user)
    try:
        address=Address.objects.get(customer=customer)
    except Address.DoesNotExist:
        address = None
    if request.method=='POST':
        form=AddressForm(request.POST,instance=address)
        if form.is_valid():
            addressline = form.cleaned_data['addressline']
            city= form.cleaned_data['city']
            postal_code = form.cleaned_data['postal_code']
            country = form.cleaned_data['country']

            try:
                response=address_validation(addressline=addressline,locality=city,postal_code=postal_code,country=country)
                if response.status_code == 200:
                    data=response.json()
                    # validationGranularity values
                    good_validation_quality=['SUB_PREMISE','PREMISE','PREMISE_PROXIMITY','ROUTE','BLOCK'] #bad quality is "OTHER"

                    #getting validationGranularity in data
                    validationGranularity = data['result']['verdict']['validationGranularity']
                    
                    #checking validationGranularity and handling data accordingly
                    if validationGranularity in good_validation_quality:
                        formatted_address = data['result']['address']['formattedAddress']
                        form_instance=form.save(commit=False)
                        form_instance.customer=customer
                        form_instance.formatted_address=formatted_address
                        form_instance.save()
                        if pk and quantity:
                            return redirect('checkout_params',pk=pk,quantity=quantity)
                        elif subtotal:
                            return redirect('checkout')
                        else:
                            return redirect('profile')
                    else:
                        # missing_part = data['result']['address']['missingComponentTypes']
                        messages.add_message(request,messages.ERROR,'Invalid address, check address\'s details')
                        form.add_error('addressline','check house number and street name')
                        form.add_error('city','check city/town')
                        form.add_error('postal_code','check postal code')
                else:
                    response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"HTTP request error: {e}")
        
        else:
            form.errors
    else:
        form = AddressForm(instance=address)
    return render(request,'shop/address.html',{'form':form})

@login_required(login_url='login')
def update_profile(request):
    customer=Customer.objects.get(user=request.user)
    if request.method=="POST":
        form=CustomUserChangeForm(request.POST,instance=request.user)
        form1=CustomerForm(request.POST,request.FILES ,instance=customer)
        if form.is_valid() and form1.is_valid():
            form.full_clean()
            form1.full_clean()
            form.save()
            form1.save()
            return redirect('profile')
        form.errors
        form1.errors
    else:        
        form=CustomUserChangeForm(instance=request.user)
        form1=CustomerForm(instance=customer)
    context={
        "form":form,
        "form1":form1,
    }
    return render(request,'shop/update_profile.html',context)


@login_required(login_url='login')
def customer_profile(request):
    
    customer=Customer.objects.get(user=request.user)
    orders=customer.order_set.all()

    context={
        'customer':customer,
        'orders':orders,
    }
    return render(request,'shop/profile.html',context)


@login_required(login_url='login')
def logoutuser(request):
    logout(request)
    return redirect('shop')




def userlogin(request):
    if request.method=='POST':
            
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('shop')
        else:
            messages.add_message(request,messages.SUCCESS ,'Username or Password is incorrect!')

    context={

    }
    return render(request,'shop/login.html',context)




def register(request):
    form=Registerationform()
    if request.method=='POST':
        form=Registerationform(request.POST)
        if form.is_valid():
            form.save()
            user=form.cleaned_data.get('username')

            messages.add_message(request,messages.SUCCESS,f'Account was created for {user}')
            return redirect('login')
    context={
        "form":form,
    }
    return render(request,"shop/register.html",context)



class ShopView(ListView):
    template_name='shop/shop.html'
    model=Laptop
    context_object_name='products'


def product_detail(request,pk):
    # checking if the product available or not
    product=get_object_or_404(Laptop,pk=pk)

    #getting cache data if any, else return empty list
    unauth_cart=cache.get('customer_cart',[])

    # handling form's data for authenticated and unauthenticated user
    if request.method=='POST':
        # getting the form's data and button
        object_quantity=int(request.POST.get('object_quantity'))
        object_id=int(request.POST.get('object_id'))
        button=request.POST.get('button')
    
        if request.user.is_authenticated:
            #getting customer's data
            customer=Customer.objects.get(user=request.user)
            customer_cart=Cart.objects.get(customer=customer)
            address=Address.objects.filter(customer=customer)
            #processing data according to the submited button
            if button=='add-to-cart':
                try:
                    product_in_cart=CartItem.objects.get(cart=customer_cart,laptop=product)
                    product_in_cart.quantity += object_quantity
                    product_in_cart.save()
                except CartItem.DoesNotExist:    
                    product_in_cart=CartItem.objects.create(cart=customer_cart,laptop=product)
                    product_in_cart.quantity=object_quantity
                    product_in_cart.price = object_quantity*product.price
                    product_in_cart.save()

                #updating product's quantity in database
                product.quantity -= object_quantity
                product.save()

                messages.add_message(request,messages.SUCCESS,'product is added to cart')
                return redirect('shop') 
            else:
                if address:
                    return redirect('checkout_params',pk=object_id,quantity=object_quantity)
                else:
                    return redirect('address_params',pk=object_id,quantity=object_quantity)
                   
        else:
            # handling the form data to unauthenticated user and store data to customer's cache 
            if button=='add-to-cart':
                is_in_cart=False
                for item in unauth_cart:
                    if object_id ==  item[0]:
                        is_in_cart=True
                        new_quantity = item[1] + object_quantity
                        if new_quantity <= product.quantity:
                            item[1] += object_quantity
                            cache.set('customer_cart',unauth_cart)
                            break
                if not is_in_cart:
                    unauth_cart.append([object_id,object_quantity])
                    cache.set('customer_cart',unauth_cart)
                context={
                    'unauth_cart':unauth_cart,
                }
                messages.add_message(request,messages.SUCCESS,'product is added to cart')
                return redirect('shop')
            else:
                return redirect('login')

    context={}
    if request.user.is_authenticated:
        customer,_=Customer.objects.get_or_create(user=request.user)
        customer_cart,_=Cart.objects.get_or_create(customer=customer)
        product_in_cart=CartItem.objects.filter(cart=customer_cart,laptop=product)
        customer_product=0
        if product_in_cart.exists():
            for item in product_in_cart:
                customer_product=item
        
        context={
        'object':product,
        'customer_product':customer_product,
        }
    

    else:
        context={
            'object':product,
            'unauth_cart':unauth_cart,
        }
        
    
    return render(request,'shop/product_detail.html',context)

        
def about(request):
    
    context={

    }
    return render(request,'shop/about.html',context)




# hx related functions

@htmx_request_only(redirect_url='shop')
def admin_customers(request):
    customers=Customer.objects.all()
    context={
        'customers':customers,
    }
    return render(request,'shop/htmx/admin_customers.html',context)

@htmx_request_only(redirect_url='shop')
def admin_orders(request):
    orders=Order.objects.all()
    total_order = sum(1 for order in orders)
    delivered_order= sum(1 for order in orders if order.status == "delivered")
    on_way_order=sum(1 for order in orders if order.status == 'on way to delivery')
    pendding_order=sum(1 for order in orders if order.status == 'pendding')
    context={
        'orders':orders,
        'total_order':total_order,
        'delivered_order':delivered_order,
        'on_way_order':on_way_order,
        'pendding_order':pendding_order,
    }
    return render(request,'shop/htmx/admin_orders.html',context)

@htmx_request_only(redirect_url='shop')
def admin_products(request):
    laptops=Laptop.objects.all()
    total_products=laptops.count()
    in_stock = sum(1 for product in laptops if product.quantity > 0)
    out_of_stock=sum(1 for product in laptops if product.quantity == 0)
   
    context={
        'laptops':laptops,
        'total_products':total_products,
        'in_stock':in_stock,
        'out_of_stock':out_of_stock,
    }
    return render(request,'shop/htmx/admin_products.html',context)


@htmx_request_only(redirect_url='shop')
def hx_ordered(request):
    #getting customer
    customer=Customer.objects.get(user=request.user)

    #getting customer's orders in descending order (from new to old)
    orders=customer.order_set.all().order_by('-date_created')
    print("orders:",orders)

    context={
        "orders":orders,
    }
    return render(request,"shop/htmx/hx_ordered.html",context)

@htmx_request_only(redirect_url='shop')
def hx_profile(request):
    
    customer=Customer.objects.get(user=request.user)
    context={
        'customer':customer,
    }
    return render(request,'shop/htmx/hx_profile.html',context)

@htmx_request_only(redirect_url='shop')
def hx_quantity_range(request,pk):
    # handling quantity select option for product_detail

    product=Laptop.objects.get(id=pk)
    quantity=product.quantity
    if request.user.is_authenticated:
        customer=Customer.objects.get(user=request.user)
        customer_cart=Cart.objects.get(customer=customer)
        try:
            product_in_cart=CartItem.objects.get(cart=customer_cart,laptop=product)
            product_quantity=product_in_cart.quantity
            numbers=list(range(0,quantity+product_quantity+1))
        except CartItem.DoesNotExist:
            numbers=list(range(0,quantity+1))
    else:
        numbers=list(range(0,quantity+1))
    
    context={
        'numbers':numbers,
        'product':product,
    }
    return render(request,'shop/htmx/quantity_range.html',context)


@htmx_request_only(redirect_url='shop')
def hx_update_cart_quantity(request):
    
    if request.user.is_authenticated:
        # getting data from the form with fetch api and handling it
        data = json.loads(request.body)
        new_quantity = data.get('new_quantity')
        object_total_quantity=data.get('total_quantity')
        object_id = data.get('object_id')

        #getting the product in database and from customer's cart
        laptop=Laptop.objects.get(id=object_id)
        customer=Customer.objects.get(user=request.user)
        customer_cart=Cart.objects.get(customer=customer)
        product_in_cart=CartItem.objects.get(cart=customer_cart,laptop=laptop)
        
        if new_quantity > 0:
            #updating product's quantity in cart
            product_in_cart.quantity=new_quantity
            product_in_cart.save()

            #updating product quantity in the database
            laptop.quantity = object_total_quantity - new_quantity
            laptop.save()


            updated_cart=customer_cart.cartitem_set.all()
            subtotal=0
            total_price=0
            for item in updated_cart:
                subtotal += item.quantity
                total_price += item.quantity * item.price        
            return JsonResponse({'subtotal':subtotal,'total_price':total_price,'new_quantity':new_quantity,'object_id':object_id})
        
        elif new_quantity == 0:
            #deleting the product in customer's cart
            laptop.quantity = object_total_quantity 
            laptop.save()
            product_in_cart.delete()

            #getting products in customer's cart
            updated_cart_quantity=customer_cart.cartitem_set.all()

            #getting subtotal and total_price in customer's cart
            subtotal=0
            total_price=0
            for item in updated_cart_quantity:
                subtotal += item.quantity
                total_price += item.quantity * item.price
            return JsonResponse({'subtotal':subtotal,'total_price':total_price,'new_quantity':new_quantity,'object_id':object_id})

                            
    elif not request.user.is_authenticated:
        # getting data from the fetch api and handle it for unauthenticated user
        data=json.loads(request.body)
        quantity = int(data.get('quantity'))
        product_id = int(data.get('objectId'))
        
        #getting customer's cart from cache
        customer_cart=cache.get('customer_cart',[])
        is_in_cart=False

        # handling quantity in customer's cart 
        for product in customer_cart:
            if product[0] == product_id:
                if quantity > 0:
                    product[1] = quantity
                    cache.set('customer_cart',customer_cart)
                    
                else:
                    customer_cart.remove(product)
                    cache.set('customer_cart',customer_cart)
                is_in_cart=True
                break
        #getting customer's cart's subtotal
        products_in_cart=sum(product[1] for product in customer_cart)

        # getting total price 
        total_price=0
        for item in customer_cart:
            laptop=Laptop.objects.get(id=item[0])
            total_price += (laptop.price * item[1])
        
        return JsonResponse({'quantity':quantity,'product_id':product_id,"products_in_cart":products_in_cart,'total_price':total_price})
    return JsonResponse('HTTP Request',safe=False)
