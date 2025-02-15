from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify

class BarInfo(models.Model):
    name = models.CharField(max_length=100, verbose_name='Bar Adı')
    logo = models.ImageField(upload_to='bar/logos/', verbose_name='Logo')
    description = RichTextField(verbose_name='Açıklama')
    hero_image = models.ImageField(upload_to='bar/hero/', verbose_name='Hero Arkaplan Görseli', blank=True, null=True)
    hero_title = models.CharField(max_length=200, verbose_name='Hero Başlık', help_text='Ana sayfadaki büyük başlık', blank=True)
    hero_subtitle = models.TextField(verbose_name='Hero Alt Başlık', help_text='Ana sayfadaki açıklama metni', blank=True)
    address = models.TextField(verbose_name='Adres')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    email = models.EmailField(verbose_name='E-posta')
    
    # Çalışma Saatleri
    monday_hours = models.CharField(max_length=50, verbose_name='Pazartesi', default='16:00 - 02:00')
    tuesday_hours = models.CharField(max_length=50, verbose_name='Salı', default='16:00 - 02:00')
    wednesday_hours = models.CharField(max_length=50, verbose_name='Çarşamba', default='16:00 - 02:00')
    thursday_hours = models.CharField(max_length=50, verbose_name='Perşembe', default='16:00 - 02:00')
    friday_hours = models.CharField(max_length=50, verbose_name='Cuma', default='16:00 - 04:00')
    saturday_hours = models.CharField(max_length=50, verbose_name='Cumartesi', default='16:00 - 04:00')
    sunday_hours = models.CharField(max_length=50, verbose_name='Pazar', default='16:00 - 02:00')
    
    class Meta:
        verbose_name = 'Bar Bilgisi'
        verbose_name_plural = 'Bar Bilgileri'
    
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

class DrinkCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Kategori Adı')
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='bar/categories/', verbose_name='Kategori Görseli', blank=True, null=True)
    description = models.TextField(verbose_name='Açıklama', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'İçecek Kategorisi'
        verbose_name_plural = 'İçecek Kategorileri'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Drink(models.Model):
    PRICE_RANGES = [
        ('low', 'Ekonomik'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
    ]

    ALCOHOL_CONTENT = [
        ('none', 'Alkolsüz'),
        ('low', 'Düşük Alkollü (%1-%5)'),
        ('medium', 'Orta Alkollü (%6-%12)'),
        ('high', 'Yüksek Alkollü (%12+)'),
    ]

    name = models.CharField(max_length=100, verbose_name='İçecek Adı')
    slug = models.SlugField(unique=True, blank=True)
    description = RichTextField(verbose_name='Açıklama')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Fiyat')
    price_range = models.CharField(max_length=10, choices=PRICE_RANGES, default='medium', verbose_name='Fiyat Aralığı')
    alcohol_content = models.CharField(max_length=10, choices=ALCOHOL_CONTENT, default='none', verbose_name='Alkol Oranı')
    image = models.ImageField(upload_to='bar/drinks/', verbose_name='İçecek Görseli')
    category = models.ForeignKey('DrinkCategory', on_delete=models.CASCADE, related_name='drinks', verbose_name='Kategori')
    is_available = models.BooleanField(default=True, verbose_name='Mevcut mu?')
    is_featured = models.BooleanField(default=False, verbose_name='Öne Çıkan')
    ingredients = models.TextField(blank=True, verbose_name='İçindekiler')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name='Ortalama Puan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'İçecek'
        verbose_name_plural = 'İçecekler'
        ordering = ['category', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.category.name}"

class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name='Etkinlik Başlığı')
    slug = models.SlugField(unique=True, blank=True)
    description = RichTextField(verbose_name='Açıklama')
    image = models.ImageField(upload_to='bar/events/', verbose_name='Etkinlik Görseli')
    date = models.DateField(verbose_name='Tarih')
    time = models.TimeField(verbose_name='Saat')
    location = models.CharField(max_length=200, verbose_name='Konum')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Bilet Fiyatı', null=True, blank=True)
    capacity = models.PositiveIntegerField(verbose_name='Kapasite', null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Etkinlik'
        verbose_name_plural = 'Etkinlikler'
        ordering = ['date', 'time']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.date}"

class Reservation(models.Model):
    name = models.CharField(max_length=100, verbose_name='Ad Soyad')
    email = models.EmailField(verbose_name='E-posta')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    date = models.DateField(verbose_name='Tarih')
    time = models.TimeField(verbose_name='Saat')
    guests = models.PositiveIntegerField(verbose_name='Kişi Sayısı')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations', verbose_name='Etkinlik')
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

class BarGallery(models.Model):
    image = models.ImageField(upload_to='bar/gallery/', verbose_name='Resim')
    title = models.CharField(max_length=100, verbose_name='Başlık', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    def __str__(self):
        return self.title or f"Galeri Resmi {self.id}"

    class Meta:
        verbose_name = 'Bar Galeri'
        verbose_name_plural = 'Bar Galeri'
        ordering = ['-created_at']

class DrinkItem(models.Model):
    name = models.CharField(max_length=100, verbose_name='İçecek Adı')
    description = models.TextField(verbose_name='Açıklama')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Fiyat')
    category = models.ForeignKey(DrinkCategory, on_delete=models.CASCADE, verbose_name='Kategori')
    image = models.ImageField(upload_to='drink_items/', null=True, blank=True, verbose_name='Görsel')
    is_featured = models.BooleanField(default=False, verbose_name='Öne Çıkan')
    price_range = models.CharField(
        max_length=10,
        choices=[('low', 'Ekonomik'), ('medium', 'Orta'), ('high', 'Yüksek')],
        default='medium',
        verbose_name='Fiyat Aralığı'
    )
    alcohol_content = models.CharField(
        max_length=10,
        choices=[('none', 'Alkolsüz'), ('low', 'Düşük'), ('medium', 'Orta'), ('high', 'Yüksek')],
        default='none',
        verbose_name='Alkol Oranı'
    )
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name='Ortalama Puan')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'İçecek'
        verbose_name_plural = 'İçecekler'
