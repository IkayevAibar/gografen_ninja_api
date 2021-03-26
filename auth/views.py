from ninja.errors import HttpError
from grafen import settings
from django.contrib.auth.hashers import check_password
# from django.contrib.auth.models import User
from app.models import User
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage, send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from ninja import Form, Router
from django.http import HttpResponse
from app import models, schemas

from auth.jwt import create_token
from app.tokens import account_activation_token

api_auth = Router()


@api_auth.post('login')
def login(request, email: str = Form(...), password: str = Form(...)):
    user = get_object_or_404(User, email=email)
    if user.check_password(password):
        return (user.id,create_token(user.id))



@api_auth.get('/user/activate/{uidb64}/{token}', tags=["users"])
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


@api_auth.post('/user/set_password/{uidb64}/{token}', tags=["users"])
def set_new_password(request, uidb64, token, password: str = Form(...), confirm_password: str = Form(...)):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if(password==confirm_password):
            user.set_password(password)
            user.save(update_fields=['password'])
        else:
            return HttpResponse('Passwords are not same.')
        # return redirect('home')
        return HttpResponse('Your password has been set. Now you can login your account.')
    else:
        return HttpResponse('Link is invalid!')


@api_auth.post("/user/password_reset", tags=["users"])
def password_reset(request,email: str = Form(...)):
    user = models.User.objects.filter(email=email).first()
    try:
        mail_subject = 'Reset your password.'
        message = render_to_string('password_reset_form.html', {
            'user':user,
            'domain': request.get_host(),
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        print(message)
        # email = EmailMessage(
        #             mail_subject, message, to=[user.email]
        # )
        # email.send()
        send_mail(
            mail_subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
    except:
        raise HttpError(422, "Введены неправильные данные(email)")
    return "Sent"
