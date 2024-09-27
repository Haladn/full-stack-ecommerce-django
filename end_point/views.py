
from .models import Laptop
from .serializers import LaptopSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework import generics

#using class based views with default mixins to retrieve and create objects
class ProductList(generics.ListCreateAPIView):
    queryset=Laptop.objects.all()
    serializer_class=LaptopSerializer
    permission_classes=[IsOwnerOrReadOnly] 

    #super user has access to write a new product
    def perform_create(self, serializer):
        if  self.request.user.is_superuser:
            serializer.save(owner=self.request.user)

   

#using class based views with default mixins to retrieve,update and delete an object
class LaptopDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Laptop.objects.all()
    serializer_class=LaptopSerializer
    permission_classes=[IsOwnerOrReadOnly] 

    #just the super_user or the creator of the object has access to update the object
    def perform_update(self,serializer):
        object=self.get_object()
        if self.request.user.is_superuser or self.request.user==object.owner:
            serializer.save(owner=self.request.user)
    #just the super_user or the creator of the object has access to delete the object
    def perform_destroy(self, instance):
        if self.request.user.is_superuser or self.request.user==instance.owner:
            instance.delete()

            
