from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class UserProfile(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    patronymic = models.CharField(max_length=100, blank=True, null=True, verbose_name='Отчество')

    def is_manager(self):
        return self.role == 'manager'
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_user(self):
        return self.role == 'user'

    def __str__(self):
        return f"{self.username}"
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Position(models.Model):
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name
    

class Doctor(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, verbose_name='Должность')
    photo = models.ImageField(upload_to='images', help_text="Добавьте фото врача", null=True, verbose_name='Фото')
    about = models.CharField(max_length=3000, verbose_name='О специалисте', null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    def __str__(self):
        return f"{self.last_name} {self.name}"

    def get_full_name(self):
        return f"{self.last_name} {self.name}"

class Service(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    doctor = models.ManyToManyField('Doctor')
    photo = models.ImageField(upload_to='images', help_text="Добавьте фото услуги", null=True)
    stoplist = models.BooleanField(verbose_name='в стоп листе', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    def __str__(self):
        return self.title
    
    
class Condition(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Appointment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Пользователь')
    name = models.CharField(max_length=150, verbose_name='Полное имя', null=True, blank=True)
    date = models.DateTimeField(null=True, verbose_name="Дата", blank=True)
    service = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True)
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Врач")
    condition = models.ForeignKey('Condition', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Статус')
    note = models.TextField(max_length=3000, null=True, blank=True, verbose_name="Заметка")
    was_rescheduled = models.BooleanField(verbose_name='перенесена', blank=True, default=False, null=True)

    def __str__(self):
        return f'Клиент: {self.user.get_full_name()}, услуга {self.service}, дата {self.date}, статус {self.condition}'
    
    # установка статуса в соответствии с датой записи
    def past(self):
        if self.condition != Condition.objects.get(pk=3):
            if self.date:
                current_datetime = timezone.now()
                if self.date > current_datetime:
                    self.condition = Condition.objects.get(pk=1)
                else:
                    self.condition = Condition.objects.get(pk=2)
    
    

class Message(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    topic = models.CharField(max_length=100, null=True, blank=True)
    text = models.CharField(max_length=3000)

    def __str__(self):
        return self.topic

class Comments(models.Model):
    name = models.CharField(max_length=100)
    text = models.CharField(max_length=3000)

    def __str__(self):
        return f'Отзыв пользователя: {self.name}'