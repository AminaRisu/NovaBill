from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from billing_app import views   # your app

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth Pages
    path('', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('forgot-password/', views.forgot_password, name='forgot'),

    # Billing Page
    path('billing/', views.billing_page, name='billing'),

    # Django Built-in Password Reset Views
    path("reset-password/",
         auth_views.PasswordResetView.as_view(
             template_name="password_reset.html"
         ),
         name="reset_password"),

    path("reset-password/done/",
         auth_views.PasswordResetDoneView.as_view(
             template_name="password_reset_sent.html"
         ),
         name="password_reset_done"),

    path("reset/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(
             template_name="password_reset_form.html"
         ),
         name="password_reset_confirm"),

    path("reset-password/complete/",
         auth_views.PasswordResetCompleteView.as_view(
             template_name="password_reset_done.html"
         ),
         name="password_reset_complete"),
]
