from django.contrib import admin
from billing import views
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('billing/', include('billing.urls', namespace='billing')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='billing/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/dashboard/', views.api_dashboard_data, name='api_dashboard_data'),

]
