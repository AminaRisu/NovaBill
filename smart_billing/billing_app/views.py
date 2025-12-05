from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


# ============================
# LOGIN PAGE
# ============================
def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("billing")
        else:
            messages.error(request, "Invalid username or password!")
            return redirect("login")   # Show error in login page only

    return render(request, "login.html")



# ============================
# SIGNUP PAGE
# ============================
def signup_page(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Username exists?
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, "signup.html")     # STAY ON SIGNUP PAGE

        # Email exists?
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return render(request, "signup.html")     # STAY ON SIGNUP PAGE

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        user.first_name = full_name
        user.save()

        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")      # Redirect to login after success

    return render(request, "signup.html")



# ============================
# FORGOT PASSWORD PAGE
# ============================
def forgot_password(request):
    return redirect("reset_password")

# ============================
# BILLING PAGE
# ============================
def billing_page(request):
    return render(request, "billing.html")
