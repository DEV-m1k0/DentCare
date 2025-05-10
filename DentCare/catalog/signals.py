# appointments/signals.py
from django.core.mail import send_mail
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Appointment
from DentCare.settings import EMAIL_HOST_USER

@receiver(pre_save, sender=Appointment)
def capture_appointment_state(sender, instance, **kwargs):
    """Capture original state before saving."""
    if instance.pk:  # Existing appointment being updated
        try:
            original = Appointment.objects.get(pk=instance.pk)
            instance._original_date = original.date
            instance._original_condition = original.condition
        except Appointment.DoesNotExist:
            pass

@receiver(post_save, sender=Appointment)
def handle_appointment_emails(sender, instance, created, **kwargs):
    """Send emails based on appointment changes."""
    user = instance.user
    if not user or not user.email:
        return  # Skip if no user/email

    if created:
        # Email for new appointment
        subject = 'Новая запись создана'
        message = (
            f'Здравствуйте, {user.get_full_name()}!\n\n'
            f'Вы успешно создали запись на услугу "{instance.service}".\n'
            f'Дата и время: {instance.date}\n'
            'Спасибо за выбор нашей клиники!'
        )
        send_mail(
            subject,
            message,
            EMAIL_HOST_USER,  # Update with your email
            [user.email],
            fail_silently=False,
        )
    else:
        # Email for date change
        original_date = getattr(instance, '_original_date', None)
        if original_date and instance.date != original_date:
            subject = 'Изменение даты записи'
            message = (
                f'Здравствуйте, {user.get_full_name()}!\n\n'
                f'Дата вашей записи на услугу "{instance.service}" изменена.\n'
                f'Новая дата и время: {instance.date}\n'
                'Пожалуйста, учтите изменения в вашем расписании.'
            )
            send_mail(
                subject,
                message,
                EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

        # Email for cancellation (Condition pk=3)
        original_condition = getattr(instance, '_original_condition', None)
        current_condition = instance.condition
        if current_condition and current_condition.pk == 3:
            if original_condition != current_condition:
                subject = 'Запись отменена'
                message = (
                    f'Здравствуйте, {user.get_full_name()}!\n\n'
                    f'Ваша запись на услугу "{instance.service}" отменена.\n'
                    'Если у вас возникли вопросы, свяжитесь с нами.'
                )
                send_mail(
                    subject,
                    message,
                    EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )

        # Cleanup
        for attr in ['_original_date', '_original_condition']:
            if hasattr(instance, attr):
                delattr(instance, attr)