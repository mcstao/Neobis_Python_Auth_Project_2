
from django.shortcuts import render, redirect
from django.views import View
from .forms import *
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

from .tokens import account_activation_token




def activateEmail(request, user, to_email):
    mail_subject = 'Активация вашего аккаунта.'
    message = render_to_string('template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Дорогой <b>{user}</b>, проверьте вашу почту <b>{to_email}</b> \
                и заверщите вашу регистрацию. <b>Note:</b> Проверьте спам если не пришло.')
    else:
        messages.error(request, f'Проблема отправки  {to_email}, проверьте правильность написания.')

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Спасибо за активацию.')
        return redirect('login')
    else:
        messages.error(request, 'Ссылка не активна')

    return redirect('home')
class Register(View):

    template_name = 'registration/register.html'



    def get(self, request):

        context = {
            'form': UserCreationForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        if request.method == "POST":
            form = UserCreationForm(request.POST)

            if form.is_valid():
                user = form.save(commit=False)
                user.is_active=False
                user.save()
                activateEmail(request, user, form.cleaned_data.get("email"))


                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
        else:
            form = UserCreationForm()
        context = {
            'form':form
        }
        return render(request, self.template_name, context)


