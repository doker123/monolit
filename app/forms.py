from django import forms
from .models import ProfileUser, Question, Choice
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .models import user_registered

# Форма для изменения информации пользователя
class ChangeUserInfoForm(forms.ModelForm):
    # Поле для электронной почты, обязательное для заполнения
    email = forms.EmailField(required=True, label='Адрес электронной почты')

    class Meta:
        # Указывает модель, с которой работает форма
        model = ProfileUser
        # Поля модели, которые будут отображаться в форме
        fields = ['username', 'email', 'first_name','avatar', 'last_name', 'send_messages']

# Форма регистрации нового пользователя
class  RegisterUserForm(forms.ModelForm):
    # Поле для загрузки аватара (необязательное)
    avatar = forms.ImageField(required=False, label='Аватар пользователя')
    # Поле для электронной почты, обязательное для заполнения
    email = forms.EmailField( required=True, label='Адресс электроной почты')
    # Поле для ввода пароля, отображается в виде скрытого поля (звездочки)
    password1 = forms.CharField(label='Пороль', widget=forms.PasswordInput, help_text= password_validation.password_validators_help_text_html())
    # Поле для повторного ввода пароля, также скрытое
    password2 = forms.CharField(label='Пороль(повторно)', widget= forms.PasswordInput, help_text= password_validation.password_validators_help_text_html())

    # Метод для валидации пароля
    def clean_password(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    # Метод для общих проверок формы (в данном случае - совпадение паролей)
    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        # Проверяем, совпадают ли пароли
        if password1 and password2 and password1 != password2:
            errors ={'password2': ValidationError(
                "Введённые данные не совпадают", code='password_mismatch')}
            raise ValidationError(errors)

    # Метод, вызываемый при сохранении формы
    def save(self, commit=True):
        # Создаём объект пользователя, но пока не сохраняем в базу данных
        user = super().save(commit=False)
        # Устанавливаем пароль (с хешированием)
        user.set_password(self.cleaned_data['password1'])
        # Устанавливаем статус неактивного пользователя
        user.is_active = False
        user.is_activated=False
        if commit:
            # Сохраняем пользователя в базу данных
            user.save()
        # Отправляем сигнал о регистрации пользователя
        user_registered.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        # Указывает модель, с которой работает форма
        model = ProfileUser
        # Поля модели, которые будут отображаться в форме (включая пароли)
        fields = ['username', 'email','password1','password2','avatar',
                  'first_name', 'last_name', 'send_messages']

# Форма для создания/редактирования вопроса
class QuestionForm(forms.ModelForm):
    class Meta:
        # Указывает модель, с которой работает форма
        model = Question
        # Поля модели, которые будут отображаться в форме
        fields = ['title', 'short_description', 'full_description', 'image']
        # Настройка виджетов (внешнего вида) для полей формы
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'full_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

# Форма для создания/редактирования варианта ответа
class ChoiceForm(forms.ModelForm):
    class Meta:
        # Указывает модель, с которой работает форма
        model = Choice
        # Поле модели, которое будет отображаться в форме
        fields = ['text']
        # Настройка виджета для поля текста
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
        }

# Форма для голосования (опционально, можно использовать просто POST-данные)
class VoteForm(forms.Form):
    # Поле для выбора варианта ответа, изначально пустое
    choice = forms.ModelChoiceField(queryset=Choice.objects.none(), widget=forms.RadioSelect)

    # Конструктор формы, позволяет передать конкретный вопрос
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ограничиваем queryset вариантами ответа, связанными с конкретным вопросом
        self.fields['choice'].queryset = question.choices.all()