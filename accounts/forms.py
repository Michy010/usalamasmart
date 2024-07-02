from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm (UserCreationForm):
    email = forms.EmailField(required=True)

    #configuration

    class Meta:
        model = User
        fields =[
            'username', 'email', 'password1', 'password2',
        ]
    
    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False) # super function is refering to Parent class
        user.email = self.cleaned_data["email"] # handling additional fields
        if commit:
            user.save()
        return user
