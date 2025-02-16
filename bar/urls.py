from django.urls import path
from . import views

app_name = 'bar'

urlpatterns = [
    path('', views.home, name='home'),
    path('drinks/', views.drinks, name='drinks'),
    path('drinks/<slug:drink_slug>/', views.drink_detail, name='drink_detail'),
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('events/', views.events, name='events'),
    path('event/<slug:event_slug>/', views.event_detail, name='event_detail'),
    path('reservation/', views.reservation, name='reservation'),
    path('reservation/success/', views.reservation_success, name='reservation_success'),
    path('search/', views.search, name='search'),
    path('contact/', views.contact, name='contact'),
] 
