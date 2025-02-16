from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import HomePageSettings, UserProfile, ContactMessage, Payment, Cart, CartItem, Order, OrderItem
from restaurant.models import RestaurantInfo, MenuItem
from bar.models import BarInfo, Drink
from django import forms
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.db.models import Avg
from .forms import UserProfileForm, CustomUserCreationForm, CustomAuthenticationForm, ContactForm
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils import timezone
import stripe
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.db import transaction

# Stripe API anahtarını ayarla
stripe.api_key = settings.STRIPE_SECRET_KEY

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label='Ad')
    last_name = forms.CharField(required=True, label='Soyad')

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

def create_user_profiles():
    users = User.objects.filter(userprofile__isnull=True)
    for user in users:
        UserProfile.objects.get_or_create(user=user)

def get_or_create_active_cart(user):
    """
    Kullanıcı için aktif sepeti alır veya oluşturur.
    Birden fazla aktif sepet varsa, en son oluşturulanı korur.
    """
    active_carts = Cart.objects.filter(user=user, is_active=True)
    if active_carts.count() > 1:
        # En son sepeti aktif tut, diğerlerini deaktif yap
        latest_cart = active_carts.latest('created_at')
        active_carts.exclude(id=latest_cart.id).update(is_active=False)
        return latest_cart
    return Cart.objects.get_or_create(user=user, is_active=True)[0]

def home(request):
    create_user_profiles()
    home_settings = HomePageSettings.objects.first()
    
    if request.user.is_authenticated:
        cart = get_or_create_active_cart(request.user)
    else:
        cart = None
    
    # Giriş yapıldıktan sonra mesaj göster
    if request.user.is_authenticated and 'just_logged_in' in request.session:
        messages.success(request, 'Hoş geldiniz! Lütfen gitmek istediğiniz sayfayı seçiniz.')
        del request.session['just_logged_in']  # Oturum değişkenini temizle
    
    context = {
        'home_settings': home_settings,
        'cart': cart,
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
def profile_view(request):
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
    
    # Siparişleri getir
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    print(f"[Profile Debug] User ID: {request.user.id}")
    print(f"[Profile Debug] Found orders count: {orders.count()}")
    for order in orders:
        print(f"[Profile Debug] Order #{order.order_number} - Amount: {order.total_amount} - Status: {order.status} - Payment ID: {order.payment_id}")

    # Ödemeleri getir
    payments = Payment.objects.filter(
        user=request.user
    ).order_by('-created_at')

    print(f"[Profile Debug] Found payments count: {payments.count()}")
    for payment in payments:
        print(f"[Profile Debug] Payment ID: {payment.id} - Amount: {payment.amount} - Status: {payment.status} - Stripe ID: {payment.stripe_payment_intent_id}")
    
    context = {
        'user': request.user,
        'orders': orders,
        'payments': payments,
    }
    
    return render(request, 'profile.html', context)

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

@login_required
def create_payment_intent(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Geçersiz istek metodu'}, status=405)
        
    try:
        # Sepeti kontrol et
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
        
        if not cart.items.exists():
            return JsonResponse({
                'error': 'Sepetiniz boş. Lütfen sepete ürün ekleyin.'
            }, status=400)
        
        # Toplam tutarı hesapla
        total_with_tax = cart.get_total_with_tax()
        
        # Minimum tutar kontrolü (0.50€)
        if total_with_tax < Decimal('0.50'):
            return JsonResponse({
                'error': 'Minimum sipariş tutarı 0.50€ olmalıdır.'
            }, status=400)
        
        # Kuruş cinsinden tutarı hesapla
        amount_in_cents = int(total_with_tax * 100)
        
        try:
            # Stripe Payment Intent oluştur
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency='eur',
                payment_method_types=['card'],
                metadata={
                    'user_id': str(request.user.id),
                    'cart_id': str(cart.id),
                    'total_items': str(cart.get_total_items())
                },
                description=f'Sipariş - {request.user.get_full_name()}',
                receipt_email=request.user.email
            )
            
            print(f"[Payment Debug] Payment Intent created: {intent.id}")
            print(f"[Payment Debug] Client Secret: {intent.client_secret}")
            
            return JsonResponse({
                'clientSecret': intent.client_secret,
                'amount': amount_in_cents,
                'currency': 'eur'
            })
            
        except stripe.error.StripeError as e:
            print(f"[Payment Debug] Stripe hatası: {str(e)}")
            return JsonResponse({
                'error': f'Ödeme işlemi başlatılamadı: {str(e)}'
            }, status=400)
            
    except Exception as e:
        print(f"[Payment Debug] Beklenmeyen hata: {str(e)}")
        return JsonResponse({
            'error': 'Ödeme işlemi başlatılırken bir hata oluştu.'
        }, status=400)

@csrf_exempt
def stripe_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Yalnızca POST istekleri kabul edilir'}, status=405)

    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        print(f"Webhook hata: {str(e)}")
        return JsonResponse({'error': 'Geçersiz payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"Webhook imza hatası: {str(e)}")
        return JsonResponse({'error': 'İmza doğrulama hatası'}, status=400)

    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        print(f"Başarılı ödeme: {payment_intent.id}")
        
        # Metadata'dan user_id ve cart_id'yi al
        user_id = payment_intent.metadata.get('user_id')
        cart_id = payment_intent.metadata.get('cart_id')
        
        if user_id and cart_id:
            try:
                # Siparişi tamamla
                user = User.objects.get(id=user_id)
                cart = Cart.objects.get(id=cart_id)
                
                # Sipariş oluştur
                order = Order.objects.create(
                    user=user,
                    total_amount=payment_intent.amount / 100,  # Cent'ten TL'ye çevir
                    payment_id=payment_intent.id,
                    status='completed'
                )
                
                # Sepet öğelerini siparişe ekle
                for item in cart.items.all():
                    if item.menu_item:
                        OrderItem.objects.create(
                            order=order,
                            menu_item=item.menu_item,
                            quantity=item.quantity,
                            price=item.menu_item.price,
                            total_price=item.get_total_price()
                        )
                    elif item.drink:
                        OrderItem.objects.create(
                            order=order,
                            drink=item.drink,
                            quantity=item.quantity,
                            price=item.drink.price,
                            total_price=item.get_total_price()
                        )
                
                # Sepeti temizle
                cart.items.all().delete()
                cart.is_active = False
                cart.save()
                
                # Yeni sepet oluştur
                Cart.objects.create(user=user, is_active=True)
                
                print(f"Sipariş başarıyla oluşturuldu: {order.id}")
                
            except (User.DoesNotExist, Cart.DoesNotExist) as e:
                print(f"Sipariş oluşturma hatası: {str(e)}")
                return JsonResponse({'error': 'Kullanıcı veya sepet bulunamadı'}, status=400)
            except Exception as e:
                print(f"Beklenmeyen hata: {str(e)}")
                return JsonResponse({'error': 'Sipariş işlenirken hata oluştu'}, status=500)
    
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        print(f"Başarısız ödeme: {payment_intent.id}")
        error_message = payment_intent.last_payment_error.message if payment_intent.last_payment_error else 'Bilinmeyen hata'
        print(f"Hata mesajı: {error_message}")
    
    return JsonResponse({'status': 'success'})

@login_required
def payment_page(request):
    cart = get_or_create_active_cart(request.user)
    
    total_with_tax = cart.get_total_with_tax()
    if total_with_tax < Decimal('0.50'):
        messages.error(request, 'Minimum sipariş tutarı 0.50€ olmalıdır.')
        return redirect('cart')
    
    stripe_public_key = settings.STRIPE_PUBLIC_KEY.strip()
    if '#' in stripe_public_key:
        stripe_public_key = stripe_public_key.split('#')[0].strip()
        
    context = {
        'STRIPE_PUBLIC_KEY': stripe_public_key,
        'cart': cart,
        'success_url': request.build_absolute_uri(reverse('payment_success')),
    }
    return render(request, 'payment.html', context)

@login_required
def payment_success(request):
    # Kullanıcının en son siparişini bul
    latest_order = Order.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-created_at').first()
    
    if latest_order:
        messages.success(request, 'Ödemeniz başarıyla tamamlandı!')
        
        # Aktif sepeti temizle
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
            cart.is_active = False
            cart.save()
            Cart.objects.create(user=request.user, is_active=True)
        except Cart.DoesNotExist:
            pass
    
    return render(request, 'payment_success.html', {
        'order': latest_order
    })

@login_required
def cart_view(request):
    cart = get_or_create_active_cart(request.user)
    restaurant_info = RestaurantInfo.objects.first()
    context = {
        'cart': cart,
        'restaurant_info': restaurant_info
    }
    return render(request, 'cart.html', context)

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Sepete ürün eklemek için giriş yapmalısınız.',
                'redirect_url': reverse('login')
            })
            
        menu_item_id = request.POST.get('menu_item_id')
        drink_id = request.POST.get('drink_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
        
        if menu_item_id:
            menu_item = MenuItem.objects.get(id=menu_item_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                menu_item=menu_item,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            item_name = menu_item.name
            
        elif drink_id:
            drink = Drink.objects.get(id=drink_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                drink=drink,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            item_name = drink.name

        # AJAX isteği ise JSON yanıtı döndür
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'{item_name} sepetinize eklendi.',
                'cart_total': cart.get_total_items()
            })
        
        # Normal form gönderimi ise sepet sayfasına yönlendir
        messages.success(request, f'{item_name} sepetinize eklendi.')
        return redirect('cart')
    
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek'})

@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
            return JsonResponse({'status': 'success'})
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ürün bulunamadı'})
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek'})

@login_required
def update_cart_item(request, item_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'error': 'Geçersiz istek metodu'}, status=405)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            return JsonResponse({'status': 'error', 'error': 'Geçersiz miktar'}, status=400)
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.quantity = quantity
        cart_item.save()
        
        # Sepet toplamlarını güncelle
        cart = cart_item.cart
        return JsonResponse({
            'status': 'success',
            'item_total': cart_item.get_total_price(),
            'cart_subtotal': cart.get_total_price(),
            'cart_tax': cart.get_tax_amount(),
            'cart_total': cart.get_total_with_tax()
        })
        
    except CartItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Ürün bulunamadı'}, status=404)
    except ValueError:
        return JsonResponse({'status': 'error', 'error': 'Geçersiz miktar formatı'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)

@login_required
def invoice_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    restaurant_info = RestaurantInfo.objects.first()
    
    # KDV tutarını hesapla (14%)
    tax_amount = order.total_amount * Decimal('0.14')
    total_amount_with_tax = order.total_amount + tax_amount
    
    context = {
        'order': order,
        'restaurant_info': restaurant_info,
        'tax_amount': tax_amount,
        'total_amount_with_tax': total_amount_with_tax
    }
    return render(request, 'invoice.html', context) 