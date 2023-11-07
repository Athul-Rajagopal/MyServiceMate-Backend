from django.core.mail import send_mail
from backend import settings
from django.core.mail import send_mail

def send_worker_notification(worker, booking):
    subject = 'New Booking Notification'
    message = f'Hello {worker.username},\n\nYou have a new booking with the following details:\n'
    message += f'Booking ID: {booking.id}\n'
    message += f'Date: {booking.date}\n'
    message += f'Contact Address: {booking.contact_address}\n'
    message += f'Issue: {booking.issue}\n\n'
    message += 'Please log in to your account for more information.\n\n'
    message += 'Thank you!\nYour ServiceMate Team'

    from_email = settings.EMAIL_HOST_USER  # Change this to your email
    recipient_list = [worker.email]  # Use the worker's email address
    
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

