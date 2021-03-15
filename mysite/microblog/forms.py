from django import forms
from django.forms import fields, EmailField
from .models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginForm(forms.Form):
    username = fields.CharField(required=True)
    password = fields.CharField(widget=forms.PasswordInput, required=True)
    remember_me = fields.BooleanField(required=False)


class EditProfileForm(forms.Form):
    username = fields.CharField(label='Username')
    about_me = fields.CharField(label='About me', min_length=0, max_length=140, required=False,
                                widget=forms.Textarea(attrs={'cols': 50, 'rows': 20}))


class RegistrationForm(forms.Form):
    username = fields.CharField(required=True, error_messages={'required': 'username cannot be empty'})
    email = fields.EmailField(required=True, error_messages={'required': 'email cannot be empty'})
    password = fields.CharField(widget=forms.PasswordInput, required=True,
                                error_messages={'required': 'password cannot be empty'})
    password2 = fields.CharField(widget=forms.PasswordInput, required=True,
                                 error_messages={'required': 'password cannot be empty'})

    def clean_username(self):
        user = User.objects.filter(username=self.cleaned_data['username']).first()
        if user is not None:
            raise ValidationError(message='Please use a different username.', code='invalid')
        else:
            return self.cleaned_data['username']

    def clean_email(self):
        user = User.objects.filter(email=self.cleaned_data['email']).first()
        if user is not None:
            raise ValidationError(message='Please use a different email address.', code='invalid')
        else:
            return self.cleaned_data['email']

    def clean_password2(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('password2'):
            raise ValidationError(message='field must be equal to password', code='invalid')
        else:
            return self.cleaned_data


class EmptyForm(forms.Form):
    pass


class PostForm(forms.Form):
    post = fields.CharField(required=True, max_length=140, min_length=1,
                            widget=forms.Textarea(attrs={'cols': 50, 'rows': 20}))

'''
class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')
        widgets = {
            'password': forms.PasswordInput()
        }

    def clean_username(self):
        user = User.objects.filter(username=self.cleaned_data['username']).first()
        if user is None:
            raise ValidationError(message='username is invalid.', code='invalid')
        else:
            return self.cleaned_data['username']

'''
'''
class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'email': forms.EmailInput(),
        }

        def clean_username(self):
            user = User.objects.filter(username=self.cleaned_data['username']).first()
            if user is not None:
                raise ValidationError(message='Please use a different username.', code='invalid')
            else:
                return self.cleaned_data['username']

        def clean_email(self):
            user = User.objects.filter(email=self.cleaned_data['email']).first()
            if user is not None:
                raise ValidationError(message='Please use a different email address.', code='invalid')
            else:
                return self.cleaned_data['email']
'''
