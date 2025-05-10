from typing import Any
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import *
# модели и формы для получения данных
from . models import Doctor, Appointment, Service, Message, Comments, Condition, UserProfile
from . forms import AppointmentCreateForm, AppointmentUpdateForm, DoctorForm
# для обработи даты
from datetime import datetime
# для работы с API
from . serializers import DoctorSerializer, ServiceSerializer, AppointmentSerializer, MessageSerializer
from rest_framework import generics
from django.contrib.auth.views import LoginView, PasswordResetView
from .forms import *
from django.contrib.auth.hashers import make_password
from django.views.generic.base import ContextMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from .tasks import send_password_reset_email


class DoctorsForUsersView(TemplateView):
    template_name = 'catalog/doctors_for_users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctors'] = Doctor.objects.all()
        return context


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin()
    
class ManagerOrAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_manager() or self.request.user.is_admin()

class MyLoginView(LoginView):
    form_class = MyAuthForm
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_manager():
            return reverse_lazy('clients')
        return reverse_lazy('index')


class RegView(CreateView):
    template_name = 'registration/register.html'
    model = UserProfile
    queryset = UserProfile.objects.all()
    form_class = RegForm
    success_url = '/login/'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            hashed_password = make_password(password)
            user.password = hashed_password
            user.save()
            return redirect(self.success_url)
        return render(request, self.template_name, {"form": form})


class ServiceDetailPageView(DetailView):
    model = Service
    template_name = 'catalog/service_detail.html'
    context_object_name = 'service'


"""Часть пользователя"""
"""Отображение страниц, данные берутся из бд"""
class IndexView(TemplateView, ContextMixin):
    template_name = 'catalog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['doctors'] = Doctor.objects.all()
        context['services'] = Service.objects.all()
        context['comments'] = Comments.objects.all()

        return context
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # if request.user.is_authenticated:
        #     if request.user.is_manager():
        #         return redirect('clients')
        #     elif request.user.is_admin():
        #         return redirect('admin_clients')
        return super().get(request, *args, **kwargs)

class MakeAppointmentView(FormView, LoginRequiredMixin):
    model = Appointment
    form_class = MakeAppointmentForm
    template_name = 'catalog/appointment.html'
    success_url = '/my_appointment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctors'] = Doctor.objects.all()
        context['services'] = Service.objects.all()
        return context

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        print("Received POST data:", request.POST)  # Debug log
        
        service_id = request.POST.get('service')
        doctor_id = request.POST.get('doctor')
        invalid_date = request.POST.get('date')
        
        print(f"Parsed data - service_id: {service_id}, doctor_id: {doctor_id}, date: {invalid_date}")  # Debug log
        
        if not all([service_id, doctor_id, invalid_date]):
            print("Missing required fields")  # Debug log
            return HttpResponseBadRequest('Missing required fields')

        try:
            valid_date = datetime.strptime(invalid_date, '%Y-%m-%dT%H:%M')
            print(f"Parsed date: {valid_date}")  # Debug log
        except ValueError:
            print("Invalid date format")  # Debug log
            return HttpResponseBadRequest('Invalid date format')

        if valid_date < datetime.now():
            print("Date is in the past")  # Debug log
            return HttpResponseBadRequest('Дата не может быть в прошлом')

        try:
            service = Service.objects.get(pk=int(service_id))
            doctor = Doctor.objects.get(pk=int(doctor_id))
            
            print(f"Found service: {service}, doctor: {doctor}")  # Debug log
            
            # Verify that the doctor is available for this service
            if doctor not in service.doctor.all():
                print(f"Doctor {doctor} is not available for service {service}")  # Debug log
                return HttpResponseBadRequest('Selected doctor is not available for this service')

            appointment = Appointment(
                user=request.user,
                service=service,
                doctor=doctor,
                date=valid_date,
                was_rescheduled=False,
                condition=Condition.objects.get(pk=1)
            )
            appointment.save()
            print(f"Created appointment: {appointment}")  # Debug log
            return redirect(self.success_url)
            
        except (Service.DoesNotExist, Doctor.DoesNotExist) as e:
            print(f"Service or Doctor not found: {str(e)}")  # Debug log
            return HttpResponseBadRequest('Invalid service or doctor')
        except Exception as e:
            print(f"Unexpected error: {str(e)}")  # Debug log
            return HttpResponseBadRequest(str(e))

def about(request):
    return render(request, 'catalog/about.html')


def contact(request):
    return render(request, 'catalog/contact.html')

def price(request):
    services = Service.objects.filter(is_active=True)
    return render(request, 'catalog/price.html', {'services': services})

def service(request):
    services = Service.objects.filter(is_active=True)
    return render(request, 'catalog/service.html', {'services': services})

class TeamView(ManagerOrAdminRequiredMixin, View):
    def get(self, request):
        doctors = Doctor.objects.all()
        return render(request, 'catalog/doctors_for_manager.html', {'doctors': doctors})

def testimonial(request):
    comments = Comments.objects.all()
    return render(request, 'catalog/testimonial.html', {'comments': comments})

class MyAppointmentView(TemplateView):
    template_name = 'catalog/my_appointment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_appointments = Appointment.objects.filter(user=self.request.user)
        context['future_appointments'] = all_appointments.filter(condition=1)
        context['cancelled_appointments'] = all_appointments.filter(condition=3)
        context['past_appointments'] = all_appointments.filter(condition=2)
        return context

class DoctorDetailView(DetailView):
    model = Doctor
    context_object_name = 'doctor'


# отправка сообщения 
def send_message(request):
    if request.method == 'POST':
        user = request.user
        topic = request.POST.get('topic')
        text = request.POST.get('text')

        try:
            message = Message.objects.create(user=user, topic=topic, text=text)
            message.save()

            return render(request, 'catalog/contact.html')
        except Exception as e:
            return render(request, 'catalog/index.html')

#поиск доктора для конкретной услуги       
def find_doctor(request):
    if request.method == 'POST':
        service_id = request.POST.get('service')

        service = Service.objects.get(pk=service_id)
        doctors = service.doctor.all()
        doctor = doctors[0]

    return HttpResponseRedirect(f'/doctor/{doctor.id}')


"""Часть администратора"""
# записи, доступные для редактирования
def appointments(request):
    appointments = Appointment.objects.all()
    for appointment in appointments:
        service = Service.objects.get(title=appointment.service)
        available_doctors = service.doctor.all() # список врачей, которые могут оказать услугу, указанную в записи
        appointment.doctor = available_doctors[0]
        appointment.past()
        appointment.save()
    appointments = Appointment.objects.filter(condition_id=1)# выбираются записи, которые ещё не состоялись и не были отменены
    print(appointments)
    context = {
        'appointments': appointments,    
               }
    return render(request, 'catalog/appointments.html', context)

# редактирование записи
class AppointmentUpdateView(ManagerOrAdminRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentUpdateForm
    template_name = 'catalog/appointment_edit_manager.html'

    def get_success_url(self):
        appointment = self.object
        return reverse_lazy('appointment-history-client', kwargs={'pk': appointment.user.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        appointment = self.get_object()
        service = appointment.service
        available_doctors = service.doctor.all()
        kwargs['available_doctors'] = available_doctors
        
        if 'instance' not in kwargs:
            kwargs['instance'] = appointment
            
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment = self.get_object()
        context['appointment'] = appointment
        return context

    def form_valid(self, form):
        # Check if the date was changed
        if form.cleaned_data['date'] != self.object.date:
            self.object.was_rescheduled = True
            messages.success(self.request, 'Запись успешно перенесена')
        else:
            messages.success(self.request, 'Запись успешно обновлена')
        return super().form_valid(form)

# Отменить запись 
@login_required
def appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    cancelled_condition = get_object_or_404(Condition, id=3)
    
    # Only allow cancellation if the appointment is in the future
    if appointment.condition.id == 1:  # Only cancel future appointments
        appointment.condition = cancelled_condition
        appointment.save()
        messages.success(request, 'Запись успешно отменена')
    else:
        messages.error(request, 'Нельзя отменить уже состоявшуюся или отмененную запись')
    
    # Redirect back to the patient history page
    return redirect('appointment-history-client', pk=appointment.user.pk)

# История записей клиента
def AppointmentHistoryClient(request, pk):
    client = get_object_or_404(UserProfile, pk=pk)
    
    # Get all appointments for the client
    all_appointments = Appointment.objects.filter(user=client)
    
    # Update appointment statuses
    for appointment in all_appointments:
        appointment.past()
        appointment.save()
    
    # Filter appointments by status
    future_appointments = all_appointments.filter(condition=1).order_by('date')
    past_appointments = all_appointments.filter(condition=2).order_by('-date')
    cancelled_appointments = all_appointments.filter(condition=3).order_by('-date')
    
    context = {
        'client': client,
        'future_appointments': future_appointments,
        'past_appointments': past_appointments,
        'cancelled_appointments': cancelled_appointments,
    }
    return render(request, 'catalog/patient_history.html', context)

# Выбрать клиента, чью историю записей просматривать
def AppointmentHistory(request):
    clients = UserProfile.objects.all()
    return render(request, 'catalog/appointment_history.html', {'clients': clients})

# Состоявшиеся записи
def show_past(request, pk):
    client = UserProfile.objects.get(pk=pk)
    past = Appointment.objects.filter(condition_id=2, user=client)
    context = {
        'past_appointments': past,
        'client': client,
    }
    return render(request, 'catalog/past.html', context)

# Отмененные записи
def show_cancelled(request, pk):
    client = UserProfile.objects.get(pk=pk)
    deleted = Appointment.objects.filter(condition_id=3, user=client)
    context = {
        'cancelled_appointments': deleted,
        'client': client,
    }
    return render(request, 'catalog/cancelled.html', context)

# Клиенты
def clients(request):
    clients = UserProfile.objects.all()
    return render(request, 'catalog/clients.html', {'clients': clients})

#список услуг
def services(request):
    if request.user.is_manager() or request.user.is_admin():
        services = Service.objects.all()
        return render(request, 'catalog/services.html', {'services': services})
    else:
        services = Service.objects.filter(is_active=True)
        return render(request, 'catalog/services.html', {'services': services})

# создать услугу
class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'catalog/service_form.html'
    success_url = reverse_lazy('services')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление услуги'
        return context

    def form_valid(self, form):
        form.instance.is_active = True
        messages.success(self.request, 'Услуга успешно добавлена')
        return super().form_valid(form)

# редактировать услугу
class ServiceUpdateView(ManagerOrAdminRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'catalog/service_form.html'
    success_url = reverse_lazy('services')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование услуги'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Услуга успешно обновлена')
        return super().form_valid(form)

# добавить услугу в стоп лист или удалить её оттуда
def stoplist(request, pk):
    service = Service.objects.get(pk=pk)
    if service.stoplist:
        service.stoplist = None
    else:
        service.stoplist = 1
    service.save()
    return redirect('services')


#API
class DoctorList(generics.ListCreateAPIView):  #создание
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class DoctorDetail(generics.RetrieveUpdateDestroyAPIView):  #получениe, обновлениe, удалениe
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class ServiceList(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class AppointmentList(generics.ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class AppointmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class MessageList(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

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

class ProfileView(TemplateView):
    template_name = 'catalog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointments'] = Appointment.objects.filter(user=self.request.user)
        return context

class ProfileEditView(UpdateView):
    model = UserProfile
    template_name = 'catalog/profile_edit.html'
    fields = ['first_name', 'last_name', 'patronymic', 'email']
    success_url = '/profile/'

    def get_object(self, queryset=None):
        return self.request.user

class AppointmentEditView(LoginRequiredMixin, UpdateView):
    model = Appointment
    template_name = 'catalog/my_appointment_edit.html'
    fields = ['date']
    success_url = reverse_lazy('my-appointment')

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user)

    def form_valid(self, form):
        action = self.request.POST.get('action')
        if action == 'cancel':
            # Get the cancelled condition (id=3)
            cancelled_condition = Condition.objects.get(id=3)
            self.object.condition = cancelled_condition
            self.object.save()
            messages.success(self.request, 'Запись успешно отменена')
            return HttpResponseRedirect(self.success_url)
        else:
            self.object.was_rescheduled = True
            messages.success(self.request, 'Дата записи успешно изменена')
            return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].fields['date'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'}
        )
        return context

class TestimonialView(TemplateView):
    template_name = 'catalog/testimonial.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comments.objects.all().order_by('-id')
        return context
    
    def post(self, request):
        comment_id = request.POST.get('comment_id')
        comment = get_object_or_404(Comments, id=comment_id)
        comment.delete()
        return redirect('testimonial')

class AddTestimonialView(LoginRequiredMixin, View):
    def post(self, request):
        text = request.POST.get('text')
        if text:
            Comments.objects.create(
                name=request.user.get_full_name(),
                text=text
            )
            messages.success(request, 'Ваш отзыв успешно добавлен!')
        return redirect('testimonial')

class DoctorUpdateView(ManagerOrAdminRequiredMixin, UpdateView):
    model = Doctor
    template_name = 'catalog/doctor_update.html'
    fields = ['name', 'last_name', 'position', 'photo', 'about', 'is_active']
    success_url = reverse_lazy('team')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование врача'
        return context

class DoctorDeactivateView(ManagerOrAdminRequiredMixin, View):
    def post(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        doctor.is_active = not doctor.is_active  # Toggle the status
        doctor.save()
        
        if doctor.is_active:
            messages.success(request, 'Врач успешно активирован')
        else:
            messages.success(request, 'Врач успешно деактивирован')
            
        return redirect('team')

class ServiceDeactivateView(ManagerOrAdminRequiredMixin, View):
    def post(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        service.is_active = not service.is_active  # Toggle the status
        service.save()
        
        if service.is_active:
            messages.success(request, 'Услуга успешно активирована')
        else:
            messages.success(request, 'Услуга успешно деактивирована')
            
        return redirect('services')

@login_required
def doctor_appointments(request):
    if not hasattr(request.user, 'doctor'):
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('index')
        
    appointments = Appointment.objects.filter(dentist=request.user.doctor)
    
    # Apply filters
    date = request.GET.get('date')
    status = request.GET.get('status')
    
    if date:
        appointments = appointments.filter(date=date)
    if status:
        appointments = appointments.filter(status=status)
    
    context = {
        'appointments': appointments
    }
    return render(request, 'catalog/doctor_appointments.html', context)

@login_required
def appointment_complete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, dentist=request.user.doctor)
    appointment.status = 'completed'
    appointment.save()
    messages.success(request, 'Прием успешно завершен')
    return redirect('doctor-appointments')

class DoctorCreateView(ManagerOrAdminRequiredMixin, CreateView):
    model = Doctor
    template_name = 'catalog/doctor_form.html'
    form_class = DoctorForm
    success_url = reverse_lazy('team')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление врача'
        return context

    def form_valid(self, form):
        form.instance.is_active = True
        messages.success(self.request, 'Врач успешно добавлен')
        return super().form_valid(form)

class DoctorsManagerView(ManagerOrAdminRequiredMixin, View):
    template_name = 'catalog/doctors_for_manager.html'
    
    def get(self, request):
        doctors = Doctor.objects.all().order_by('name', 'last_name')
        context = {
            'doctors': doctors,
            'title': 'Управление врачами'
        }
        return render(request, self.template_name, context)

class AllUsersView(AdminRequiredMixin, ListView):
    model = UserProfile
    template_name = 'catalog/all_users.html'
    context_object_name = 'users'
    ordering = ['-date_joined']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Все пользователи'
        return context

class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = UserProfile
    success_url = reverse_lazy('admin_all-users')
    template_name = 'catalog/all_users.html'

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            messages.error(request, 'Вы не можете удалить свой собственный аккаунт')
            return redirect('admin_all-users')
        messages.success(request, f'Пользователь {user.get_full_name()} успешно удален')
        return super().delete(request, *args, **kwargs)

class UserEditView(AdminRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'catalog/user_edit.html'
    fields = ['first_name', 'last_name', 'patronymic', 'email', 'role', 'is_active']
    success_url = reverse_lazy('admin_all-users')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование пользователя'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Пользователь успешно обновлен')
        return super().form_valid(form)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = UserProfile.objects.get(email=email)
            # Schedule the email sending task
            send_password_reset_email(email, user.id)
            return super().form_valid(form)
        except UserProfile.DoesNotExist:
            # If user doesn't exist, still show success message for security
            return super().form_valid(form)