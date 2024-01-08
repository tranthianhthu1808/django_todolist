from django.shortcuts import render, redirect
from .models import Todo
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth.forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .decorators import user_not_authentianed


# Create your views here.

def index(request):
    todo = Todo.objects.all()

    if request.method == 'POST':
        new_todo = Todo(
            title = request.POST['title']
        )
        new_todo.save()
        return redirect('/')
    return render(request, 'app/index.html', {'todos': todo})

# def index(request):
#     return render(request, 'app/index.html')

def delete(request, pk):
    todo = Todo.objects.get(id=pk)
    todo.delete()
    return redirect('/')

# Create your views here.
# def register(request):
#     form = CreateUserForm()
#     if request.method == "POST":
#         form = CreateUserForm(request.POST)
#         if form.is_valid():
#             form.save()
#     context = {'form': form}
#     return render(request, 'app/register.html', context)
# def login_page(request):
#     # if request.user.is_authenticated:
#     #     return redirect('index.html')
#     # if request.method == "POST":
#     #     username = request.POST.get('username')
#     #     password = request.POST.get('password')
#     #     user = authenticate(request, username = username, password = password)
#     #     if user is not None:
#     #         login(request, user)
#     #         return redirect('index.html')
#     #     else:
#     #         messages.info(request,'UserName or Password is incorrect!')
#     # context = {}
#     return render(request, 'app/login.html')

# def logout_page(request):
#     # logout(request)
#     # return render(request,'app/login.html')
#     pass
############################################################
def register(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"New account created: {user.username}")
            return redirect('/')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = UserCreationForm()

    return render(
        request=request,
        template_name="app/register.html",
        context={"form": form}
        )
@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return render(request, 'app/logout.html')

def custom_login(request):
    if request.user.is_authenticated:
        return redirect("/")

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
                return redirect("/")

        else:
            for error in list(form.errors.values()):
                messages.error(request, error) 

    form = AuthenticationForm()

    return render(
        request=request,
        template_name="app/login.html",
        context={"form": form}
        )
