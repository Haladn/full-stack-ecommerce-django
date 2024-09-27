
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django import forms
from django.contrib.auth.models import User
from .models import Address,Customer,Order
from end_point.models import Laptop
from django.forms import MultiValueField
from django.core.validators import RegexValidator
from django.forms import MultiWidget, TextInput,Select,Widget,widgets


class OrderForm(forms.ModelForm):
    class Meta:
        model=Order
        fields="__all__"
        # fields=['total_price','quantity','status']
        # exclude=['laptop','customer']


class Registerationform(UserCreationForm):
    class Meta:
        model=User
        fields=['username','email','password1','password2']

class LaptopForm(forms.ModelForm):
    class Meta:
        model=Laptop
        fields="__all__"



class PhoneFieldWidget(MultiWidget):
    # modifing widgets to define a select and textinput fields
    COUNTRIES=(
        ('----------','----------'),
        ('0044','UK +44'),
        ('001','US +1'),
        ('0033','FR +33'),
        ('0049','GER +49')
        )
    def __init__(self, attrs=None):
        widgets = (
            Select(choices=self.COUNTRIES),
            TextInput(),
        )
        super().__init__(widgets, attrs)

    # calling decompress method to separate single input value
    def decompress(self, value):
        if value:
            return value.split(' ')
        return [None, None]

class PhoneField(MultiValueField):
    def __init__(self, **kwargs):
        error_messages = {
            "incomplete": "Enter a country calling code and a phone number.",
        }
        fields = (
            forms.CharField(
                error_messages={"incomplete": "Select a country calling code."},
                validators=[
                    RegexValidator(r"^[0-9  a-z A-Z +]+$", "Enter a valid country calling code."),
                ],
            ),
            forms.CharField(
                error_messages={"incomplete": "Enter a phone number."},
                validators=[RegexValidator(r"^[0-9]+$", "Enter a valid phone number.")],
                max_length=10,min_length=9
            ),
        )
        widget = PhoneFieldWidget()

        #calling parent init methode to override it with custome one
        super().__init__(
            error_messages=error_messages,
            fields=fields,
            widget=widget,
            require_all_fields=False,
            **kwargs
        )
    
    def compress(self, data_list):
        return " ".join(data_list)


class AddressForm(forms.ModelForm):
    phone_number=PhoneField()
    class Meta:
        model=Address
        fields=['phone_number','first_name','last_name','country','building_name','addressline','city','postal_code',]

        #it's be a best practice to exclude the model instance if we don't
        #  then we have to render it to the template to handle the form validation process error
        exclude=['customer','formatted_address']


        
class CustomUserChangeForm(UserChangeForm):
    email=forms.EmailField(required=True)
    class Meta:
        model=User
        fields=('username','email','first_name','last_name')


class CustomerForm(forms.ModelForm):
    
    class Meta:
        model=Customer
        fields=['profile_pic']  
