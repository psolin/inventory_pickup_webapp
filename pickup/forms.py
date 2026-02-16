from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import Transaction, Item


class EditProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_num', 'transaction_date', 'est_pickup_date', 'customer_name', 'phone']


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['transaction_num', 'desc']
