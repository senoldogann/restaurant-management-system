from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import BarInfo, DrinkCategory, Drink, Event, Reservation, BarGallery
from foodanddrink.models import Cart, CartItem
from .forms import ReservationForm, EventReservationForm
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required

def home(request):
    bar_info = BarInfo.objects.first()
    today = timezone.now().date()
    featured_drinks = Drink.objects.filter(is_featured=True, is_available=True)[:6]
    categories = DrinkCategory.objects.filter(is_active=True)[:4]
    upcoming_events = Event.objects.filter(
        is_active=True,
        date__gte=today
    ).order_by('date', 'time')[:3]
    gallery_images = BarGallery.objects.filter(is_active=True)
    
    # Hero image için CSS değişkeni
    if bar_info and bar_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{bar_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'bar_info': bar_info,
        'featured_drinks': featured_drinks,
        'categories': categories,
        'upcoming_events': upcoming_events,
        'hero_image_style': hero_image_style,
        'today': today,
        'gallery_images': gallery_images,
    }
    return render(request, 'bar/home.html', context)

def drinks(request):
    bar_info = BarInfo.objects.first()
    categories = DrinkCategory.objects.filter(is_active=True)
    drinks = Drink.objects.filter(is_available=True).select_related('category')
    
    # Hero image için CSS değişkeni
    if bar_info and bar_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{bar_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'bar_info': bar_info,
        'categories': categories,
        'drinks': drinks,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'bar/drinks.html', context)

def category_detail(request, category_slug):
    bar_info = BarInfo.objects.first()
    category = get_object_or_404(DrinkCategory, slug=category_slug, is_active=True)
    drinks = Drink.objects.filter(category=category, is_available=True)
    
    # Hero image için CSS değişkeni
    if bar_info and bar_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{bar_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'bar_info': bar_info,
        'category': category,
        'drinks': drinks,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'bar/category_detail.html', context)

def drink_detail(request, drink_slug):
    bar_info = BarInfo.objects.first()
    drink = get_object_or_404(Drink, slug=drink_slug, is_available=True)
    
    # Hero image için CSS değişkeni
    if bar_info and bar_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{bar_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'bar_info': bar_info,
        'drink': drink,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'bar/drink_detail.html', context)

def events(request):
    bar_info = BarInfo.objects.first()
    today = timezone.now().date()
    
    # Gelecek etkinlikleri al ve tarihe göre sırala
    upcoming_events = Event.objects.filter(
        is_active=True,
        date__gte=today
    ).order_by('date', 'time')
    
    # Geçmiş etkinlikleri al ve tarihe göre tersten sırala
    past_events = Event.objects.filter(
        is_active=True,
        date__lt=today
    ).order_by('-date', '-time')
    
    # İki listeyi birleştir (gelecek etkinlikler önce)
    events = list(upcoming_events) + list(past_events)
    
    # En son eklenen etkinliği bul
    latest_event = Event.objects.filter(is_active=True).order_by('-created_at').first()
    
    # Hero image için CSS değişkeni
    if bar_info and bar_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{bar_info.hero_image.url}"); }}</style>'
    elif latest_event and latest_event.image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{latest_event.image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'bar_info': bar_info,
        'events': events,
        'today': today,
        'hero_image_style': hero_image_style,
        'latest_event': latest_event,
    }
    return render(request, 'bar/events.html', context)

def event_detail(request, event_slug):
    bar_info = BarInfo.objects.first()
    today = timezone.now().date()
    event = get_object_or_404(Event, slug=event_slug)
    
    # Eğer etkinlik tarihi geçmişse özel 404 sayfasını göster
    if event.date < today:
        context = {
            'bar_info': bar_info,
            'hero_image_style': f'<style>:root {{ --hero-image: url("{event.image.url if event.image else ""}"); }}</style>' if event.image else '',
        }
        return render(request, 'bar/404.html', context, status=404)
    
    # Sadece gelecek etkinlikleri göster
    other_events = Event.objects.filter(
        is_active=True,
        date__gte=today
    ).exclude(id=event.id).order_by('date', 'time')[:3]
    
    # Hero image için CSS değişkeni
    if bar_info and bar_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{bar_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'bar_info': bar_info,
        'event': event,
        'other_events': other_events,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'bar/event_detail.html', context)

def reservation(request):
    bar_info = BarInfo.objects.first()
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rezervasyonunuz başarıyla alınmıştır. En kısa sürede size dönüş yapacağız.')
            return redirect('bar:reservation_success')
    else:
        form = ReservationForm()
    
    # Hero image için CSS değişkeni
    if bar_info and bar_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{bar_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'form': form,
        'bar_info': bar_info,
        'upcoming_events': Event.objects.filter(is_active=True).order_by('date', 'time')[:5],
        'hero_image_style': hero_image_style,
    }
    return render(request, 'bar/reservation.html', context)

def reservation_success(request):
    bar_info = BarInfo.objects.first()
    
    # Hero image için CSS değişkeni
    if bar_info and bar_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{bar_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'bar_info': bar_info,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'bar/reservation_success.html', context)

def search(request):
    bar_info = BarInfo.objects.first()
    query = request.GET.get('q', '')
    
    drinks = []
    events = []
    
    if query:
        drinks = Drink.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query),
            is_available=True
        )
        
        today = timezone.now().date()
        events = Event.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query),
            is_active=True,
            date__gte=today
        )
    
    # Hero image için CSS değişkeni
    if bar_info and bar_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{bar_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'bar_info': bar_info,
        'query': query,
        'drinks': drinks,
        'events': events,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'bar/search.html', context)

def contact(request):
    bar_info = BarInfo.objects.first()
    
    # Hero image için CSS değişkeni
    if bar_info and bar_info.hero_image:
        hero_image_style = f'<style>:root {{ --hero-image: url("{bar_info.hero_image.url}"); }}</style>'
    else:
        hero_image_style = ''
    
    context = {
        'bar_info': bar_info,
        'hero_image_style': hero_image_style,
    }
    return render(request, 'bar/contact.html', context)
