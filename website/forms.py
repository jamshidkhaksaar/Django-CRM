# website/forms.py
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Record, CustomUser

class SignUpForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class AddRecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = [
            'transaction_type',
            'item_name',
            'item_type',
            'description',
            'project',
            'location',
            'unit_measure',
            'quantity',
            'unit_price',
            'total_value',
            'date',
            'reviewer',
            'reviewer_result',
            'approval',
            'cashier_status'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'quantity': forms.NumberInput(attrs={'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01'}),
            'total_value': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required as needed
        for field in self.fields:
            if field not in ['comments']:  # Add other optional fields here
                self.fields[field].required = True
            # Add Bootstrap classes to all fields
            self.fields[field].widget.attrs['class'] = 'form-control'