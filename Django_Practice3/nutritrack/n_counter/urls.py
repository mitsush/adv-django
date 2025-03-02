from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('delete/<int:id>/', views.delete_consume, name='delete'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='app/login.html', next_page='index'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('add-food/', views.add_food, name='add_food'),  # Changed to match template URLs
    path('update-goals/', views.update_goals, name='update_goals'),  # Changed to match template URLs
    path('chart-data/', views.chart_data, name='chart-data'),
]