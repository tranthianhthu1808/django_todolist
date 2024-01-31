from django.shortcuts import render, redirect, get_object_or_404
from .models import Todo
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .forms import UserLoginForm, UserRegistrationForm, UserUpdateForm
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.db.models.query_utils import Q
from datetime import datetime, timedelta
from django.contrib.auth.models import User


# Create your views here.
#to do manage
def index(request): 
    # todo = Todo.objects.filter()
    # if request.method == 'POST':
    #     new_todo = Todo(
    #         title = request.POST['title'],
    #         finish_date = request.POST['finish_date']
    #     )
    #     new_todo.save()
    #     return redirect('index')
    # return render(request, 'app/index.html', {'todos': todo})
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to continue your work!')
        return redirect('login')  # Thay 'login' bằng URL đến trang đăng nhập của bạn

    todos = Todo.objects.filter(user=request.user)

    if request.method == 'POST':
        new_todo = Todo(
            title=request.POST['title'],
            finish_date=request.POST['finish_date'],
            
            user=request.user
        )
        new_todo.save()
        return redirect('index')

    return render(request, 'app/index.html', {'todos': todos})

def delete(request, pk):
    todo = Todo.objects.get(id=pk)
    todo.delete()
    return redirect('/')




# def update_todo(request, todo_id):
#     # Lấy todo cần cập nhật hoặc trả về 404 nếu không tìm thấy
#     todo = get_object_or_404(Todo, id=todo_id, user=request.user)

#     if request.method == 'POST':
#         # Nếu là POST request, xử lý dữ liệu form được submit
#         form = TodoUpdateForm(request.POST, instance=todo)
#         if form.is_valid():
#             form.save()
#             return redirect('index')  # Chuyển hướng về trang danh sách todo sau khi cập nhật
    # else:
    #     # Nếu là GET request, hiển thị form với dữ liệu hiện tại của todo
    #     form = TodoUpdateForm(instance=todo)

    # return render(request, 'app/update_todo.html', {'form': form, 'todo': todo})
################ User ################
def register(request):
    # if request.method == "POST":
    #     form = UserRegistrationForm(request.POST)
    #     if form.is_valid():
    #         user = form.save(commit=False)
    #         user.is_active=False
    #         user.save()
    #         activateEmail(request, user, form.cleaned_data.get('email'))
    #         return redirect('/')

    #     else:
    #         for error in list(form.errors.values()):
    #             messages.error(request, error)

    # else:
    #     form = UserRegistrationForm()

    # return render(
    #     request=request,
    #     template_name="user/register.html",
    #     context={"form": form}
    #     )
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            
            # Check if the email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered.')
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                activateEmail(request, user, email)
                return redirect('/')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = UserRegistrationForm()

    return render(
        request=request,
        template_name="app/register.html",
        context={"form": form}
    )
@login_required
################### logout user #############################
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return render(request, 'app/logout.html')

################## login user #############################
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Hello <b>{user.username}</b>! You have been logged in")
                return redirect('/')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error) 

    form = AuthenticationForm()

    return render(
        request=request,
        template_name="app/login.html",
        context={"form": form}
        )

############ user activate ##############
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('/')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('/')

def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("app/template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
                received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')
#################################################################
# other things 
#################### user info ############
def profile(request, username):
    if request.method == "POST":
        user = request.user
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user_form = form.save()
            messages.success(request, f'{user_form.username}, Your profile has been updated!')
            return redirect("profile", user_form.username)

        for error in list(form.errors.values()):
            messages.error(request, error)

    user = get_user_model().objects.filter(username=username).first()
    if user:
        form = UserUpdateForm(instance=user)
        # form.fields['description'].widget.attrs = {'rows': 1}
        return render(
            request=request,
            template_name="app/profile.html",
            context={"form": form}
            )
    
    return redirect("/")

######### unauth homepage ############
def unauth_home(request):
    if request.user.is_authenticated:
        return render(request, 'app/todo_list.html')
    return render(request, 'main/home.html')
    
####################### change password ################
def password_change(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return render(request, 'app/pass_reset_confirm.html', {'form': form})


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("app/template_pass_reset.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                        """
                        <h2>Password reset sent</h2><hr>
                        <p>
                            We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                            You should receive them shortly.<br>If you don't receive an email, please make sure you've entered the address 
                            you registered with, and check your spam folder.
                        </p>
                        """
                    )
                else:
                    messages.error(request, "Problem sending reset password email, <b>SERVER PROBLEM</b>")

            return redirect('/')

    form = PasswordResetForm()
    return render(
        request=request, 
        template_name="app/pass_reset.html", 
        context={"form": form}
        )

def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in </b> now.")
                return redirect('/')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render(request, 'app/pass_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("/")
