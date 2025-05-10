from django import forms
from .models import Doctor, Service, Appointment, UserProfile, Comments, Condition
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class MakeAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'date']
        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-select bg-light border-0',
                'style': 'height: 55px;',
                'name': 'service',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': "form-control bg-light border-0",
                'style': 'height: 55px;',
                'type': 'datetime-local'
            })
        }


class RegForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'patronymic', 'username', 'email', 'password']

        widgets = {
            'password': forms.PasswordInput(attrs={
                'placeholder': 'Пароль',
                'class': 'form-control bg-light border-0',
                'style': "height: 55px;"
            }),
            'username': forms.TextInput(attrs={
                'placeholder': 'Имя пользователя',
                'class': 'form-control bg-light border-0',
                'style': "height: 55px;"
            }),
            'email': forms.TextInput(attrs={
                'placeholder': 'Почта',
                'class': 'form-control bg-light border-0',
                'style': "height: 55px;"
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Имя',
                'class': 'form-control bg-light border-0',
                'style': "height: 55px;"
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Фамилия',
                'class': 'form-control bg-light border-0',
                'style': "height: 55px;"
            }),
            'patronymic': forms.TextInput(attrs={
                'placeholder': 'Отчество',
                'class': 'form-control bg-light border-0',
                'style': "height: 55px;"
            }),
        }


class MyAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs = {
            'placeholder': 'Имя пользователя',
            'class': 'form-control bg-light border-0',
            'style': "height: 55px;"
        }
        self.fields['password'].widget.attrs = {
            'placeholder': 'Пароль',
            'class': 'form-control bg-light border-0',
            'style': "height: 55px;"
        }

# class UserRegisterForm(UserCreationForm):
#     email = forms.EmailField()
#     class Meta:
#         model = UserProfile
#         fields = ['first_name', 'last_name', 'patronymic', 'username', 'email', 'password1', 'password2', ]

class AppointmentCreateForm(forms.ModelForm):
   
    class Meta:
        model = Appointment
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class AppointmentUpdateForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'height: 60px; padding: 0.75rem 1rem;',
        }),
        required=False,
        label="Врач"
    )

    class Meta:
        model = Appointment
        fields = ['date', 'service', 'doctor', 'note']
        widgets = {
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'style': 'height: 60px; padding: 0.75rem 1rem;',
                'type': 'datetime-local',
                'placeholder': 'Выберите дату и время'
            }),
            'service': forms.Select(attrs={
                'class': 'form-select',
                'style': 'height: 60px; padding: 0.75rem 1rem;',
                'placeholder': 'Выберите услугу'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'style': 'height: 120px; padding: 0.75rem 1rem; resize: none;',
                'placeholder': 'Введите дополнительные заметки',
                'rows': 4
            })
        }

    def __init__(self, *args, available_doctors=None, **kwargs):
        super().__init__(*args, **kwargs)
        if available_doctors is not None:
            self.fields['doctor'].queryset = available_doctors
        
        # Format the initial date value if it exists
        if self.instance and self.instance.date:
            self.initial['date'] = self.instance.date.strftime('%Y-%m-%dT%H:%M')
        
        # Add custom classes and attributes to all fields
        for field_name, field in self.fields.items():
            if field_name != 'doctor':  # Skip doctor field as it's already styled
                if isinstance(field.widget, forms.TextInput):
                    field.widget.attrs.update({
                        'class': 'form-control',
                        'style': 'height: 60px; padding: 0.75rem 1rem;'
                    })
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs.update({
                        'class': 'form-select',
                        'style': 'height: 60px; padding: 0.75rem 1rem;'
                    })
                elif isinstance(field.widget, forms.Textarea):
                    field.widget.attrs.update({
                        'class': 'form-control',
                        'style': 'height: 120px; padding: 0.75rem 1rem; resize: none;'
                    })

    def save(self, commit=True):
        appointment = super().save(commit=False)
        appointment.doctor = self.cleaned_data['doctor']
        if commit:
            appointment.save()
        return appointment


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['name', 'last_name', 'position', 'photo', 'about']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя врача'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию врача'
            }),
            'position': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Выберите должность'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'about': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите информацию о враче',
                'rows': 4
            })
        }
        labels = {
            'name': 'Имя',
            'last_name': 'Фамилия',
            'position': 'Должность',
            'photo': 'Фотография',
            'about': 'О враче'
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'price', 'photo', 'doctor']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название услуги',
                'style': 'height: 45px;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите описание услуги',
                'rows': 4,
                'style': 'resize: none;'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите стоимость услуги',
                'style': 'height: 45px;',
                'min': '0'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'doctor': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'style': 'height: 150px;'
            })
        }
        labels = {
            'title': 'Название услуги',
            'description': 'Описание услуги',
            'price': 'Стоимость (₽)',
            'photo': 'Фотография услуги',
            'doctor': 'Врачи, оказывающие услугу'
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Стоимость не может быть отрицательной')
        return price

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise forms.ValidationError('Название услуги должно содержать минимум 3 символа')
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) < 10:
            raise forms.ValidationError('Описание должно содержать минимум 10 символов')
        return description


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'service', 'date', 'note', 'condition']
        widgets = {
            'doctor': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Выберите врача'
            }),
            'service': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Выберите услугу'
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'placeholder': 'Выберите дату и время'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите дополнительные заметки',
                'rows': 3
            }),
            'condition': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Выберите статус'
            })
        }
        labels = {
            'doctor': 'Врач',
            'service': 'Услуга',
            'date': 'Дата и время',
            'note': 'Заметки',
            'condition': 'Статус'
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['name', 'text']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше имя'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваш отзыв',
                'rows': 4
            })
        }
        labels = {
            'name': 'Имя',
            'text': 'Отзыв'
        }

