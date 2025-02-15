from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import HomePageSettings, Review, ReviewResponse, UserProfile, ContactMessage
from restaurant.models import RestaurantInfo
from bar.models import BarInfo
from restaurant.models import MenuItem
from bar.models import Drink
from django import forms
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.db.models import Avg
from .forms import UserProfileForm, ReviewForm
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils import timezone

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label='Ad')
    last_name = forms.CharField(required=True, label='Soyad')

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

class RestaurantReviewForm(forms.ModelForm):
    item_name = forms.ModelChoiceField(
        queryset=MenuItem.objects.all(),
        label='Yemek Seçin',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Review
        fields = ['item_name', 'rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': '1',
                'max': '5',
                'class': 'form-control'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Deneyiminizi paylaşın...'
            })
        }

class BarReviewForm(forms.ModelForm):
    item_name = forms.ModelChoiceField(
        queryset=Drink.objects.all(),
        label='İçecek Seçin',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Review
        fields = ['item_name', 'rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': '1',
                'max': '5',
                'class': 'form-control'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Deneyiminizi paylaşın...'
            })
        }

def create_user_profiles():
    users = User.objects.filter(userprofile__isnull=True)
    for user in users:
        UserProfile.objects.get_or_create(user=user)

def home(request):
    create_user_profiles()  # Mevcut kullanıcılar için profil oluştur
    home_settings = HomePageSettings.objects.first()
    
    # Giriş yapıldıktan sonra mesaj göster
    if request.user.is_authenticated and 'just_logged_in' in request.session:
        messages.success(request, 'Hoş geldiniz! Lütfen gitmek istediğiniz sayfayı seçiniz.')
        del request.session['just_logged_in']  # Oturum değişkenini temizle
    
    context = {
        'home_settings': home_settings,
    }
    return render(request, 'home.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            if not request.POST.get('terms'):
                messages.error(request, 'Kullanım koşulları ve gizlilik politikasını kabul etmelisiniz.')
                return render(request, 'registration/register.html', {'form': form})
            user = form.save()
            request.session['registration_success'] = True
            messages.success(request, 'Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        profile = user.userprofile

        # Kullanıcı bilgilerini güncelle
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()

        # Profil bilgilerini güncelle
        profile.phone_number = request.POST.get('phone_number', '')
        profile.bio = request.POST.get('bio', '')

        # Profil fotoğrafını güncelle
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, 'Profiliniz başarıyla güncellendi!')
        return redirect('profile')
    
    context = {
        'user': request.user
    }

    # Admin kullanıcıları için yanıtları getir
    if request.user.is_staff:
        responses = ReviewResponse.objects.filter(
            responded_by=request.user
        ).select_related('review', 'review__user').order_by('-created_at')
        context['responses'] = responses
    else:
        # Normal kullanıcılar için değerlendirmeleri getir
        reviews = Review.objects.filter(
            user=request.user
        ).order_by('-created_at')
        context['reviews'] = reviews
    
    return render(request, 'profile.html', context)

@login_required
def add_review(request, item_id=None):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        location = request.POST.get('location')
        item_name = request.POST.get('item_name')
        
        if not all([rating, comment, location, item_name]):
            messages.error(request, 'Tüm alanları doldurun.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        # Kullanıcının daha önce yaptığı değerlendirmeyi kontrol et
        existing_review = Review.objects.filter(
            user=request.user,
            item_name=item_name,
            location=location
        ).first()
        
        if existing_review:
            # Mevcut değerlendirmeyi güncelle
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.is_approved = True  # Güncellenen değerlendirmeyi de onaylı yap
            existing_review.save()
            message = 'Değerlendirmeniz başarıyla güncellendi.'
        else:
            # Yeni değerlendirme oluştur
            Review.objects.create(
                user=request.user,
                item_name=item_name,
                location=location,
                rating=rating,
                comment=comment,
                is_approved=True  # Otomatik onaylama
            )
            message = 'Değerlendirmeniz başarıyla kaydedildi.'
        
        messages.success(request, message)
        
        # Yönlendirme için ürünü bul
        if location == 'restaurant':
            item = MenuItem.objects.filter(name=item_name).first()
            if item:
                return redirect('restaurant:menu_item_detail', slug=item.slug)
        else:
            item = Drink.objects.filter(name=item_name).first()
            if item:
                return redirect('bar:drink_detail', slug=item.slug)
        
        return redirect('home')
    
    return HttpResponseNotAllowed(['POST'])

@login_required
@staff_member_required
def add_response(request, review_id):
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id)
        response_text = request.POST.get('response_text', '').strip()
        
        if not response_text:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'error': 'Yanıt metni boş olamaz.'
                })
            else:
                messages.error(request, 'Yanıt metni boş olamaz.')
                return redirect(request.META.get('HTTP_REFERER', '/'))
        
        response = ReviewResponse.objects.create(
            review=review,
            response_text=response_text,
            responded_by=request.user
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Yanıtınız başarıyla eklendi.',
                'response': {
                    'text': response.response_text,
                    'responder_name': response.responded_by.get_full_name(),
                    'created_at': response.created_at.strftime('%d.%m.%Y')
                }
            })
        else:
            messages.success(request, 'Yanıtınız başarıyla eklendi.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return HttpResponseNotAllowed(['POST'])

@login_required
@staff_member_required
def edit_response(request, response_id):
    response = get_object_or_404(ReviewResponse, id=response_id)
    
    if request.method == 'POST':
        response_text = request.POST.get('response_text', '').strip()
        
        if not response_text:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'error': 'Yanıt metni boş olamaz.'
                })
            else:
                messages.error(request, 'Yanıt metni boş olamaz.')
                return redirect(request.META.get('HTTP_REFERER', '/'))
        
        response.response_text = response_text
        response.is_edited = True
        response.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Yanıtınız başarıyla güncellendi.',
                'response': {
                    'text': response.response_text,
                    'responder_name': response.responded_by.get_full_name(),
                    'created_at': response.created_at.strftime('%d.%m.%Y'),
                    'updated_at': response.updated_at.strftime('%d.%m.%Y'),
                    'is_edited': response.is_edited
                }
            })
        else:
            messages.success(request, 'Yanıtınız başarıyla güncellendi.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return HttpResponseNotAllowed(['POST'])

@login_required
@staff_member_required
def delete_response(request, response_id):
    response = get_object_or_404(ReviewResponse, id=response_id)
    
    if request.method == 'POST':
        response.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Yanıt başarıyla silindi.'
            })
        else:
            messages.success(request, 'Yanıt başarıyla silindi.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return HttpResponseNotAllowed(['POST'])

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Sadece kendi değerlendirmesini silebilir
    if review.user != request.user:
        messages.error(request, 'Bu işlem için yetkiniz yok.')
        return redirect('home')
    
    item_location = review.location
    item_name = review.item_name
    review.delete()
    
    messages.success(request, 'Değerlendirmeniz başarıyla silindi.')
    
    # Ürün sayfasına yönlendir
    if item_location == 'restaurant':
        item = MenuItem.objects.filter(name=item_name).first()
        if item:
            return redirect('restaurant:menu_item_detail', slug=item.slug)
    else:
        item = Drink.objects.filter(name=item_name).first()
        if item:
            return redirect('bar:drink_detail', slug=item.slug)
    
    return redirect('home')

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Sadece kendi değerlendirmesini düzenleyebilir
    if review.user != request.user:
        messages.error(request, 'Bu işlem için yetkiniz yok.')
        return redirect('home')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not all([rating, comment]):
            messages.error(request, 'Tüm alanları doldurun.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        review.rating = rating
        review.comment = comment
        review.save()
        
        messages.success(request, 'Değerlendirmeniz başarıyla güncellendi.')
        
        # Ürün sayfasına yönlendir
        if review.location == 'restaurant':
            item = MenuItem.objects.filter(name=review.item_name).first()
            if item:
                return redirect('restaurant:menu_item_detail', slug=item.slug)
        else:
            item = Drink.objects.filter(name=review.item_name).first()
            if item:
                return redirect('bar:drink_detail', slug=item.slug)
        
        return redirect('home')
    
    return HttpResponseNotAllowed(['POST'])

class CustomLoginView(LoginView):
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            # Oturum tarayıcı kapandığında sonlanacak
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        # Kullanıcı "Beni Hatırla"yı seçtiyse, settings.py'deki SESSION_COOKIE_AGE kullanılacak
        
        # Giriş başarılı mesajı için session değişkeni
        self.request.session['just_logged_in'] = True
        
        return super().form_valid(form)

def get_restaurant_info():
    return RestaurantInfo.objects.first()

def contact(request):
    restaurant_info = RestaurantInfo.objects.first()
    bar_info = BarInfo.objects.first()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.')
            return redirect('contact')
        else:
            messages.error(request, 'Lütfen tüm alanları doldurun.')
    
    return render(request, 'contact.html', {
        'restaurant_info': restaurant_info,
        'bar_info': bar_info
    }) 