from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify

class RestaurantInfo(models.Model):
    name = models.CharField(max_length=100, verbose_name='Restoran Adı')
    logo = models.ImageField(upload_to='restaurant/logos/', verbose_name='Logo')
    description = RichTextField(verbose_name='Açıklama')
    hero_image = models.ImageField(upload_to='restaurant/hero/', verbose_name='Hero Arkaplan Görseli', blank=True, null=True)
    hero_title = models.CharField(max_length=200, verbose_name='Hero Başlık', help_text='Ana sayfadaki büyük başlık', blank=True)
    hero_subtitle = models.TextField(verbose_name='Hero Alt Başlık', help_text='Ana sayfadaki açıklama metni', blank=True)
    address = models.TextField(verbose_name='Adres')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    email = models.EmailField(verbose_name='E-posta')
    
    # Çalışma Saatleri
    monday_hours = models.CharField(max_length=50, verbose_name='Pazartesi', default='09:00 - 22:00')
    tuesday_hours = models.CharField(max_length=50, verbose_name='Salı', default='09:00 - 22:00')
    wednesday_hours = models.CharField(max_length=50, verbose_name='Çarşamba', default='09:00 - 22:00')
    thursday_hours = models.CharField(max_length=50, verbose_name='Perşembe', default='09:00 - 22:00')
    friday_hours = models.CharField(max_length=50, verbose_name='Cuma', default='09:00 - 22:00')
    saturday_hours = models.CharField(max_length=50, verbose_name='Cumartesi', default='10:00 - 23:00')
    sunday_hours = models.CharField(max_length=50, verbose_name='Pazar', default='10:00 - 23:00')
    
    class Meta:
        verbose_name = 'Restoran Bilgisi'
        verbose_name_plural = 'Restoran Bilgileri'
    
    def __str__(self):
        return self.name

    def get_working_hours(self):
        hours_dict = {
            'Pazartesi': self.monday_hours,
            'Salı': self.tuesday_hours,
            'Çarşamba': self.wednesday_hours,
            'Perşembe': self.thursday_hours,
            'Cuma': self.friday_hours,
            'Cumartesi': self.saturday_hours,
            'Pazar': self.sunday_hours,
        }
        
        # Saatleri grupla
        grouped_hours = {}
        current_hours = None
        days_group = []
        
        for day, hours in hours_dict.items():
            if hours != current_hours:
                if days_group:
                    key = f"{days_group[0]}-{days_group[-1]}" if len(days_group) > 1 else days_group[0]
                    grouped_hours[key] = current_hours
                days_group = [day]
                current_hours = hours
            else:
                days_group.append(day)
        
        # Son grubu ekle
        if days_group:
            key = f"{days_group[0]}-{days_group[-1]}" if len(days_group) > 1 else days_group[0]
            grouped_hours[key] = current_hours
        
        return grouped_hours

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Kategori Adı')
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='restaurant/categories/', verbose_name='Kategori Görseli', blank=True, null=True)
    description = models.TextField(verbose_name='Açıklama', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    PRICE_RANGES = [
        ('low', 'Ekonomik'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
    ]

    ALLERGEN_CHOICES = [
        ('gluten', 'Gluten İçerir'),
        ('lactose', 'Laktoz İçerir'),
        ('nuts', 'Fındık/Kuruyemiş İçerir'),
        ('vegan', 'Vegan'),
        ('vegetarian', 'Vejetaryen'),
    ]

    name = models.CharField(max_length=100, verbose_name='Ürün Adı')
    slug = models.SlugField(unique=True, blank=True)
    description = RichTextField(verbose_name='Ürün Açıklaması')
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Fiyat (€)')
    price_range = models.CharField(max_length=10, choices=PRICE_RANGES, default='medium', verbose_name='Fiyat Aralığı')
    image = models.ImageField(upload_to='menu_items/', verbose_name='Ürün Görseli')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Kategori')
    is_available = models.BooleanField(default=True, verbose_name='Stokta Var mı?')
    is_featured = models.BooleanField(default=False, verbose_name='Öne Çıkan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name='Ortalama Puan')
    allergens = models.JSONField(default=list, blank=True, null=True, verbose_name='Alerjenler')
    calories = models.PositiveIntegerField(null=True, blank=True, verbose_name='Kalori')
    preparation_time = models.PositiveIntegerField(null=True, blank=True, verbose_name='Hazırlama Süresi (dakika)')
    ingredients = models.TextField(blank=True, verbose_name='İçindekiler')
    dietary_restrictions = models.JSONField(default=list, blank=True, verbose_name='Diyet Gereksinimleri')

    class Meta:
        verbose_name = 'Menü Öğesi'
        verbose_name_plural = 'Menü Öğeleri'
        ordering = ['category', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.price}€"

class Reservation(models.Model):
    name = models.CharField(max_length=100, verbose_name='Ad Soyad')
    email = models.EmailField(verbose_name='E-posta')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    date = models.DateField(verbose_name='Tarih')
    time = models.TimeField(verbose_name='Saat')
    guests = models.PositiveIntegerField(verbose_name='Kişi Sayısı')
    notes = models.TextField(verbose_name='Notlar', blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Beklemede'),
            ('confirmed', 'Onaylandı'),
            ('cancelled', 'İptal Edildi')
        ],
        default='pending',
        verbose_name='Durum'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Rezervasyon'
        verbose_name_plural = 'Rezervasyonlar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.date} {self.time}"

class RestaurantGallery(models.Model):
    image = models.ImageField(upload_to='restaurant/gallery/', verbose_name='Resim')
    title = models.CharField(max_length=100, verbose_name='Başlık', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    def __str__(self):
        return self.title or f"Galeri Resmi {self.id}"

    class Meta:
        verbose_name = 'Restaurant Galeri'
        verbose_name_plural = 'Restaurant Galeri'
        ordering = ['-created_at']
