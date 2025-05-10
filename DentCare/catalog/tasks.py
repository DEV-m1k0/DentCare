from background_task import background
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@background(schedule=1)
def send_password_reset_email(user_email, user_id):
    """
    Background task to send password reset email
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Render email content
        context = {
            'user': user,
            'protocol': 'https' if settings.SECURE_SSL_REDIRECT else 'http',
            'domain': settings.DOMAIN,
            'uid': uid,
            'token': token,
        }
        
        # Render email templates
        subject = render_to_string('registration/password_reset_subject.txt', context).strip()
        message = render_to_string('registration/password_reset_email.html', context)
        
        # Log the attempt
        logger.info(f"Attempting to send password reset email to {user_email}")
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info(f"Successfully sent password reset email to {user_email}")
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
    except Exception as e:
        logger.error(f"Error sending password reset email: {str(e)}")
        raise  # Re-raise the exception to ensure the task is marked as failed 