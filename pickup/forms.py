from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# Sign Up Form
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    email = forms.EmailField(max_length=254, help_text='Enter a valid email address')

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]
from django import forms
from .models import Transaction, Item

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_num', 'transaction_date', 'est_pickup_date', 'customer_name', 'phone']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['transaction_num', 'desc']
