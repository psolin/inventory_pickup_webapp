from django import forms
from pickup.models import Transaction

class AddTransactionForm(forms.ModelForm):

	class Meta:
	# Provide an association between the ModelForm and a model
		model = Transaction
		exclude = []