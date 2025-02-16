from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import RestaurantInfo, Category, MenuItem, Reservation, RestaurantGallery
from foodanddrink.models import Cart, CartItem
from .forms import ReservationForm
from django.contrib.auth.decorators import login_required

def home(request):
    restaurant_info = RestaurantInfo.objects.first()
    featured_items = MenuItem.objects.filter(is_featured=True, is_available=True)[:6]
    gallery_images = RestaurantGallery.objects.filter(is_active=True)[:6]
    categories = Category.objects.filter(is_active=True)[:4]
    
    # Hero image için CSS değişkeni
    if restaurant_info and restaurant_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{restaurant_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'restaurant_info': restaurant_info,
        'featured_items': featured_items,
        'categories': categories,
        'hero_image_style': hero_image_style,
        'gallery_images': gallery_images,
    }
    return render(request, 'restaurant/home.html', context)

def menu(request):
    restaurant_info = RestaurantInfo.objects.first()
    categories = Category.objects.filter(is_active=True)
    menu_items = MenuItem.objects.filter(is_available=True).select_related('category')
    
    # Hero image için CSS değişkeni
    if restaurant_info and restaurant_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{restaurant_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'restaurant_info': restaurant_info,
        'categories': categories,
        'menu_items': menu_items,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'restaurant/menu.html', context)

def category_detail(request, category_slug):
    restaurant_info = RestaurantInfo.objects.first()
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    menu_items = MenuItem.objects.filter(category=category, is_available=True)
    
    # Hero image için CSS değişkeni
    if restaurant_info and restaurant_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{restaurant_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'restaurant_info': restaurant_info,
        'category': category,
        'menu_items': menu_items,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'restaurant/category_detail.html', context)

def menu_item_detail(request, slug):
    restaurant_info = RestaurantInfo.objects.first()
    item = get_object_or_404(MenuItem, slug=slug)
    
    # Hero image için CSS değişkeni
    if restaurant_info and restaurant_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{restaurant_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'restaurant_info': restaurant_info,
        'item': item,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'restaurant/menu_item_detail.html', context)

def reservation(request):
    restaurant_info = RestaurantInfo.objects.first()
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.status = 'pending'  # Varsayılan durumu 'beklemede' olarak ayarla
            reservation.save()
            messages.success(request, 'Rezervasyonunuz başarıyla alınmıştır. En kısa sürede size dönüş yapacağız.')
            return redirect('restaurant:reservation_success')
    else:
        form = ReservationForm()
    
    # Hero image için CSS değişkeni
    if restaurant_info and restaurant_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{restaurant_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'form': form,
        'restaurant_info': restaurant_info,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'restaurant/reservation.html', context)

def reservation_success(request):
    restaurant_info = RestaurantInfo.objects.first()
    
    # Hero image için CSS değişkeni
    if restaurant_info and restaurant_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{restaurant_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'restaurant_info': restaurant_info,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'restaurant/reservation_success.html', context)

def search(request):
    restaurant_info = RestaurantInfo.objects.first()
    query = request.GET.get('q', '')
    
    menu_items = []
    categories = []
    
    if query:
        menu_items = MenuItem.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query),
            is_available=True
        )
        
        categories = Category.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        )
    
    # Hero image için CSS değişkeni
    if restaurant_info and restaurant_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{restaurant_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'restaurant_info': restaurant_info,
        'query': query,
        'menu_items': menu_items,
        'categories': categories,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'restaurant/search.html', context)
