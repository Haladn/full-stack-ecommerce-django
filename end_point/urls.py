from django.urls import path
from .views import LaptopDetail,ProductList


urlpatterns=[
   path('',ProductList.as_view()),
   path('product_detail/<str:pk>/',LaptopDetail.as_view()),
    
]
