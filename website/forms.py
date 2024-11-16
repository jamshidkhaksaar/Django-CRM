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

class SignUpForm(forms.ModelForm):
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
        exclude = ("user",)
        widgets = {
            'transaction_type': forms.Select(choices=Record.TRANSACTION_TYPE_CHOICES, attrs={'class': 'form-control'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'item_type': forms.Select(choices=Record.ITEM_TYPE_CHOICES, attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Item Specification/Description'}),
            'project': forms.Select(choices=Record.PROJECT_CHOICES, attrs={'class': 'form-control'}),
            'location': forms.Select(choices=Record.LOCATION_CHOICES, attrs={'class': 'form-control'}),
            'requester': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Requester'}),
            'unit_measure': forms.Select(choices=Record.UNIT_MEASURE_CHOICES, attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Unit Price (AFN)', 'step': '0.01'}),
            'total_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total Value (AFN)', 'step': '0.01', 'readonly': 'readonly'}),
            'date': forms.DateField(
                widget=forms.DateInput(
                    attrs={
                        'type': 'date',
                        'class': 'form-control date-picker'
                    }
                )
            ),
            'reviewer': forms.Select(choices=Record.REVIEWER_CHOICES, attrs={'class': 'form-control'}),
            'reviewer_result': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reviewers Result'}),
            'approval': forms.Select(choices=Record.APPROVAL_CHOICES, attrs={'class': 'form-control'}),
            'cashier_status': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cashier Status'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Suggestions and Comments'}),
        }
    class Meta:
        model = Record
        exclude = ("user",) 