from django.contrib import admin
from .models import BarInfo, DrinkCategory, Drink, Event, Reservation, BarGallery

@admin.register(BarInfo)
class BarInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name', 'phone', 'email')
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'logo', 'description')
        }),
        ('Hero Bölümü', {
            'fields': ('hero_image', 'hero_title', 'hero_subtitle')
        }),
        ('İletişim Bilgileri', {
            'fields': ('address', 'phone', 'email')
        }),
        ('Çalışma Saatleri', {
            'fields': (
                'monday_hours', 'tuesday_hours', 'wednesday_hours',
                'thursday_hours', 'friday_hours', 'saturday_hours',
                'sunday_hours'
            )
        })
    )

@admin.register(DrinkCategory)
class DrinkCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Drink)
class DrinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'price_range', 'alcohol_content', 'is_available', 'is_featured', 'average_rating')
    list_filter = ('category', 'is_available', 'is_featured', 'price_range', 'alcohol_content')
    search_fields = ('name', 'description', 'ingredients')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('average_rating',)
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'category', 'description', 'price', 'price_range', 'image')
        }),
        ('İçecek Detayları', {
            'fields': ('alcohol_content', 'ingredients')
        }),
        ('Durum', {
            'fields': ('is_available', 'is_featured')
        }),
        ('Değerlendirme', {
            'fields': ('average_rating',),
            'classes': ('collapse',)
        })
    )

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'price', 'capacity', 'is_active')
    list_filter = ('is_active', 'date', 'created_at')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active', 'price', 'capacity')
    readonly_fields = ('created_at',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time', 'guests', 'event', 'status', 'created_at')
    list_filter = ('status', 'date', 'event', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at',)
    list_editable = ('status',)

@admin.register(BarGallery)
class BarGalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)
