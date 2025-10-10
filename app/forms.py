from django import forms
from .models import ProfileUser
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .models import user_registered

class ChangeUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')

    class Meta:
        model = ProfileUser
        fields = ['username', 'email', 'first_name','avatar', 'last_name', 'send_messages']

class  RegisterUserForm(forms.ModelForm):
    avatar = forms.ImageField(required=True, label='Аватар пользователя')
    email = forms.EmailField( required=True, label='Адресс электроной почты')
    password1 = forms.CharField(label='Пороль', widget=forms.PasswordInput, help_text= password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пороль(повторно)', widget= forms.PasswordInput, help_text= password_validation.password_validators_help_text_html())

    def clean_password(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors ={'password2': ValidationError(
                "Введённые данные не совпадают", code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.avatar = True
        user.is_active = False
        user.is_activated=False
        if commit:
            user.save()
        user_registered.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = ProfileUser
        fields = ['username', 'email','password1','password2','avatar',
                  'first_name', 'last_name', 'send_messages']