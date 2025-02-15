from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('menu/<slug:slug>/', views.menu_item_detail, name='menu_item_detail'),
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('reservation/', views.reservation, name='reservation'),
    path('reservation/success/', views.reservation_success, name='reservation_success'),
    path('search/', views.search, name='search'),
] 
