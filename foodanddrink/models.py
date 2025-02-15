from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from restaurant.models import MenuItem
from bar.models import Drink
from django.db.models import Avg

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

class Review(models.Model):
    LOCATION_CHOICES = [
        ('restaurant', 'Restoran'),
        ('bar', 'Bar'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Kullanıcı')
    location = models.CharField(max_length=10, choices=LOCATION_CHOICES, verbose_name='Mekan')
    item_name = models.CharField(max_length=100, verbose_name='Yemek/İçecek Adı')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Puan'
    )
    comment = models.TextField(verbose_name='Yorum')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yorum Tarihi')
    is_approved = models.BooleanField(default=False, verbose_name='Onaylandı')

    class Meta:
        verbose_name = 'Değerlendirme'
        verbose_name_plural = 'Değerlendirmeler'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.item_name} Değerlendirmesi'

@receiver(post_save, sender=Review)
def update_item_rating(sender, instance, **kwargs):
    # İlgili ürünü bul
    if instance.location == 'restaurant':
        item = MenuItem.objects.filter(name=instance.item_name).first()
        if item:
            # Ortalama puanı hesapla
            avg_rating = Review.objects.filter(
                location='restaurant',
                item_name=item.name
            ).aggregate(Avg('rating'))['rating__avg']
            # Ortalama puanı güncelle (None ise 0 olarak ayarla)
            item.average_rating = round(avg_rating, 2) if avg_rating is not None else 0
            item.save()
    else:  # Bar
        item = Drink.objects.filter(name=instance.item_name).first()
        if item:
            # Ortalama puanı hesapla
            avg_rating = Review.objects.filter(
                location='bar',
                item_name=item.name
            ).aggregate(Avg('rating'))['rating__avg']
            # Ortalama puanı güncelle (None ise 0 olarak ayarla)
            item.average_rating = round(avg_rating, 2) if avg_rating is not None else 0
            item.save()

class ReviewResponse(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='responses', verbose_name='Değerlendirme')
    response_text = models.TextField(verbose_name='Yanıt')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yanıt Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Düzenlenme Tarihi')
    is_edited = models.BooleanField(default=False, verbose_name='Düzenlendi mi?')
    responded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Yanıtlayan')

    class Meta:
        verbose_name = 'Değerlendirme Yanıtı'
        verbose_name_plural = 'Değerlendirme Yanıtları'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.review.item_name} Değerlendirmesine Yanıt'

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