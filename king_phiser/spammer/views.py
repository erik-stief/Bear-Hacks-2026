# my_app/views.py
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
#from .models import 

def spam_home(request):
    return render(request, 'spammer/index.html')

def send_duplicate_email_view(request, customer_id):
    # 1. Retrieve the email from the database
    # get_object_or_404 safely handles cases where the ID doesn't exist
    customer = get_object_or_404(Customer, id=customer_id)
    recipient_email = customer.email

    # 2. Prepare the pre-drafted email
    subject = "fih"
    message = ("Get King Pished!")
    from_email = settings.EMAIL_HOST_USER

    # 3. Send the email twice to the retrieved recipient
    for i in range(100):
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False, # Set to True in production if you don't want app crashes on email failure
        )

    return HttpResponse("Successfully king phished that guy.")

