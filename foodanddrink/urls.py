"""
URL configuration for foodanddrink project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('restaurant/', include('restaurant.urls')),
    path('bar/', include('bar.urls')),
    path('contact/', views.contact, name='contact'),
    path('review/<int:item_id>/', views.add_review, name='add_review'),
    path('review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/response/', views.add_response, name='add_response'),
    path('response/<int:response_id>/edit/', views.edit_response, name='edit_response'),
    path('response/<int:response_id>/delete/', views.delete_response, name='delete_response'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
