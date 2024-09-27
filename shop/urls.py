from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns=[
    path('',views.ShopView.as_view(),name='shop'),
    path("product_detail/<str:pk>/",views.product_detail,name='product_detail'),
    path('register',views.register,name='register'),
    path('login',views.userlogin,name='login'),
    path('profile',views.customer_profile,name='profile'),
    path('logout',views.logoutuser,name='logout'),
    path('about',views.about, name='about'),
    path('cart',views.CartView.as_view(), name='cart'),
    path('checkout',views.checkout,name='checkout'),
    path('checkout/<int:pk>/<int:quantity>',views.checkout,name='checkout_params'),
    path('address/<subtotal>/',views.address,name='address_subtotal'),
    path('address',views.address,name='address'),
    path('address/<int:pk>/<int:quantity>/',views.address,name='address_params'),
    path('paymentcomplete',views.paymentComplete, name='payment'),
    path('paymentcomplete/<int:pk>/<int:quantity>/',views.paymentComplete, name='payment_params'),
    path('update_profile',views.update_profile, name='update_profile'),
    path('admin',views.admin_dashboard,name='admin'),
    path('update_order/<int:pk>/',views.admin_update_orders,name='update_order_params'),
    path('update_order/',views.admin_update_orders,name='update_order'),
    path('update_product/<int:pk>/',views.admin_update_product,name="update_product_params"),
    path('update_product/',views.admin_update_product,name="update_product"),
    path('update_customer/<int:pk>/',views.admin_update_customer,name="update_customer"),
    path('add_customer/',views.admin_add_customer,name="add_customer"),
    

    
      
]

#htmx 
urlpatterns +=[
    path('hx_quantity_range/<str:pk>/',views.hx_quantity_range,name='hx_quantity_range'),
    path('hx_ordered',views.hx_ordered,name='ordered'),
    path('hx_profile',views.hx_profile,name='hx_profile'),
    path('hx_update_quantity',views.hx_update_cart_quantity,name='update_quantity'),
    path('admin_products',views.admin_products,name="admin_products"),
    path('admin_orders',views.admin_orders,name='admin_orders'),
    path('admin_customers',views.admin_customers,name='admin_customers'),
]

# password reset

urlpatterns+=[
    
  path('reset_password/', auth_views.PasswordResetView.as_view(template_name='shop/password_reset.html'), name ='reset_password'),
  path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='shop/reset_password_sent.html'), name ='password_reset_done'),
  path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='shop/password_reset_confirm.html'), name ='password_reset_confirm'),
  path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='shop/password_reset_complete.html'), name ='password_reset_complete'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
