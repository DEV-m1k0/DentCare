import os
import django

# Установите настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DentCare.settings")  # замените на имя вашего проекта
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def send_test_email():
    subject = 'Тестовое письмо'
    message = 'Это тестовое сообщение.'
    from_email = settings.DEFAULT_FROM_EMAIL  # Используйте адрес отправителя из настроек
    recipient_list = ['nngicvg9nv@illubd.com']  # Замените на адрес получателя

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print("Письмо успешно отправлено!")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")

if __name__ == "__main__":
    send_test_email()
