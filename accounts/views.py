from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.core.mail import send_mail
from django.shortcuts import redirect, render


def login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            error = "Invalid username or password."

    return render(request, "accounts/login.html", {"error": error})


def register_view(request):
    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)

        if user.email:
            send_mail(
                "Welcome to Swoop",
                f"Hi {user.username},\n\nWelcome to Swoop! You can now buy, sell, wishlist, and promote listings.\n\nThanks for joining us.",
                None,
                [user.email],
                fail_silently=True,
            )

        return redirect("dashboard")

    return render(request, "accounts/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")
