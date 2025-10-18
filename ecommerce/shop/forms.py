from django import forms
from .models import CustomUser,Orders

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'user_type']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")

        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class OrderForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = '__all__'
        widgets = {
            'expiration_date': forms.TextInput(attrs={'placeholder': 'MM/YY'}),
        }