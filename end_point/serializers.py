from rest_framework import serializers
from .models import Laptop
from django.contrib.auth.models import User


class LaptopSerializer(serializers.ModelSerializer):
    owner=serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model=Laptop
        fields=['owner','id','description','image','href','price','resolution','weight','color','system','model','cpu','quantity','category']

