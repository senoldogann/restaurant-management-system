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
from .views import home, register, profile_view, CustomLoginView, contact
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('restaurant/', include('restaurant.urls')),
    path('bar/', include('bar.urls')),
    path('contact/', contact, name='contact'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('payment/', views.payment_page, name='payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('invoice/<str:order_number>/', views.invoice_view, name='invoice'),
]

# Debug modunda static ve media dosyalarını sun
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production modunda da media dosyalarını sun
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
