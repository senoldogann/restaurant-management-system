from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from restaurant.models import MenuItem
from bar.models import Drink
from django.db.models import Avg
from django.utils import timezone
from ckeditor.fields import RichTextField
from decimal import Decimal

class HomePageSettings(models.Model):
    restaurant_background = models.ImageField(upload_to='backgrounds/', verbose_name='Restoran Arkaplan Görseli', blank=True, null=True)
    bar_background = models.ImageField(upload_to='backgrounds/', verbose_name='Bar Arkaplan Görseli', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Son Güncelleme')

    def save(self, *args, **kwargs):
        if HomePageSettings.objects.exists() and not self.pk:
            # Eğer başka bir kayıt varsa ve bu yeni bir kayıtsa, eski kaydı güncelle
            old_settings = HomePageSettings.objects.first()
            self.pk = old_settings.pk
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Anasayfa Ayarları'
        verbose_name_plural = 'Anasayfa Ayarları'

    def __str__(self):
        return 'Anasayfa Ayarları'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name='Profil Fotoğrafı')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Hakkında')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefon Numarası')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Kayıt Tarihi')

    class Meta:
        verbose_name = 'Kullanıcı Profili'
        verbose_name_plural = 'Kullanıcı Profilleri'

    def __str__(self):
        return f'{self.user.username} Profili'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name='Ad Soyad')
    email = models.EmailField(verbose_name='E-posta')
    subject = models.CharField(max_length=200, verbose_name='Konu')
    message = models.TextField(verbose_name='Mesaj')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Gönderim Tarihi')
    is_read = models.BooleanField(default=False, verbose_name='Okundu mu?')
    is_answered = models.BooleanField(default=False, verbose_name='Yanıtlandı mı?')
    answer = models.TextField(blank=True, null=True, verbose_name='Yanıt')
    answered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='answered_messages',
        verbose_name='Yanıtlayan'
    )
    answered_at = models.DateTimeField(null=True, blank=True, verbose_name='Yanıt Tarihi')
    
    class Meta:
        verbose_name = 'İletişim Mesajı'
        verbose_name_plural = 'İletişim Mesajları'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_payment_intent_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Beklemede'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
        ('refunded', 'İade Edildi')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency}"

class Campaign(models.Model):
    title = models.CharField(max_length=200, verbose_name='Kampanya Başlığı')
    description = models.TextField(verbose_name='Kampanya Açıklaması')
    discount_percentage = models.IntegerField(verbose_name='İndirim Yüzdesi')
    start_date = models.DateTimeField(verbose_name='Başlangıç Tarihi')
    end_date = models.DateTimeField(verbose_name='Bitiş Tarihi')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Kampanya'
        verbose_name_plural = 'Kampanyalar'

    def __str__(self):
        return self.title

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date 

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Kullanıcı')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')

    class Meta:
        verbose_name = 'Sepet'
        verbose_name_plural = 'Sepetler'

    def __str__(self):
        return f"{self.user.username}'in Sepeti"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def get_tax_amount(self):
        # Finlandiya'da yemek sektörü için KDV oranı %14
        return round(self.get_total_price() * Decimal('0.14'), 2)

    def get_total_with_tax(self):
        # Finlandiya KDV oranı ile toplam hesaplama
        return round(self.get_total_price() * Decimal('1.14'), 2)

    def has_minimum_amount(self):
        # Minimum sipariş tutarını 0.50€ olarak güncelleme
        return self.get_total_with_tax() >= Decimal('0.50')

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, verbose_name='Sepet')
    menu_item = models.ForeignKey('restaurant.MenuItem', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Menü Öğesi')
    drink = models.ForeignKey('bar.Drink', on_delete=models.CASCADE, null=True, blank=True, verbose_name='İçecek')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Miktar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Sepet Öğesi'
        verbose_name_plural = 'Sepet Öğeleri'

    def __str__(self):
        return f"{self.get_item_name()} ({self.quantity})"

    def get_item_name(self):
        return self.menu_item.name if self.menu_item else self.drink.name

    def get_item_price(self):
        return self.menu_item.price if self.menu_item else self.drink.price

    def get_total_price(self):
        return self.get_item_price() * self.quantity 

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Kullanıcı')
    order_number = models.CharField(max_length=20, unique=True, verbose_name='Sipariş Numarası')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Durum')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Toplam Tutar')
    payment_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='Ödeme ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Sipariş Tarihi')

    class Meta:
        verbose_name = 'Sipariş'
        verbose_name_plural = 'Siparişler'
        ordering = ['-created_at']

    def __str__(self):
        return f"Sipariş #{self.order_number}"

    def generate_order_number(self):
        return f"ORD{self.created_at.strftime('%Y%m%d')}{self.id:04d}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Önce kaydet ki ID oluşsun
            super().save(*args, **kwargs)
            # Sonra sipariş numarasını oluştur ve tekrar kaydet
            self.order_number = self.generate_order_number()
            self.save(update_fields=['order_number'])
        else:
            super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Sipariş')
    menu_item = models.ForeignKey('restaurant.MenuItem', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Menü Öğesi')
    drink = models.ForeignKey('bar.Drink', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='İçecek')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Miktar')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Birim Fiyat')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Toplam Fiyat')

    class Meta:
        verbose_name = 'Sipariş Öğesi'
        verbose_name_plural = 'Sipariş Öğeleri'

    def __str__(self):
        item_name = self.menu_item.name if self.menu_item else self.drink.name
        return f"{item_name} ({self.quantity}x)"

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs) 