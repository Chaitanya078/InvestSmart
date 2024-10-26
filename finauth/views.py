from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError

from .utils import generate_token  


from django.core.mail import EmailMessage
from django.conf import settings 


import threading


class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message

    def run(self):
        self.email_message.send()


def signup(request):
    if request.method == "POST":
        username = request.POST['email']
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']
        
        if password != confirm_password:
            messages.warning(request, "Password is not matching")
            return render(request, 'auth/signup.html')

        if User.objects.filter(username=username).exists():
            messages.warning(request, "Email is taken")
            return render(request, 'auth/signup.html')

        myuser = User.objects.create_user(username=username, email=username, password=password)
        myuser.is_active = False
        myuser.save()
        current_site = get_current_site(request)
        email_subject = "Activate your account"
        message = render_to_string('finauth/activate.html', {
            'user': myuser,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })

        email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [username])
        EmailThread(email_message).start()
      
        messages.info(request, "Activate your Account")
        return redirect('/finauth/login')

    return render(request, 'auth/signup.html')


class ActivateAccountView(View):
    def get(self, request, uidb64, token):  # Corrected here
        try:
            uid = force_bytes(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            user = None
            
        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.info(request, "Account activated successfully")
            return redirect('/finauth/login')
        
        return render(request, 'auth/activate.html')


def handlelogin(request):
    if request.method == "POST":
        username = request.POST['email']
        userpassword = request.POST['pass1']
        
        myuser = authenticate(request, username=username, password=userpassword)

        if myuser is not None:
            login(request, myuser)
            messages.success(request, "Login successful!")
            return render(request, 'index.html')  

        else:
            messages.error(request, "Invalid credentials")
            return redirect('/finauth/login')

    return render(request, 'auth/login.html')


def handlelogout(request):
    logout(request)
    messages.success(request, "Logout Success")
    return redirect('/finauth/login')
