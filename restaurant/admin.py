from django.contrib import admin
from .models import RestaurantInfo, Category, MenuItem, Reservation, RestaurantGallery
from django import forms

class MenuItemAdminForm(forms.ModelForm):
    allergens = forms.MultipleChoiceField(
        choices=MenuItem.ALLERGEN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Alerjenler'
    )

    class Meta:
        model = MenuItem
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.allergens:
            self.initial['allergens'] = self.instance.allergens

    def clean_allergens(self):
        return list(self.cleaned_data['allergens'])

@admin.register(RestaurantInfo)
class RestaurantInfoAdmin(admin.ModelAdmin):
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

    def has_add_permission(self, request):
        # Sadece bir tane RestaurantInfo kaydı olabilir
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    form = MenuItemAdminForm
    list_display = ('name', 'category', 'price', 'is_available', 'is_featured', 'average_rating')
    list_filter = ('category', 'is_available', 'is_featured', 'price_range')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('average_rating',)
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'category', 'description', 'price', 'price_range', 'image')
        }),
        ('Durum', {
            'fields': ('is_available', 'is_featured')
        }),
        ('Detaylar', {
            'fields': ('ingredients', 'calories', 'preparation_time', 'allergens')
        }),
        ('Değerlendirme', {
            'fields': ('average_rating',),
            'classes': ('collapse',)
        })
    )

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'date', 'time', 'guests', 'status', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at',)

@admin.register(RestaurantGallery)
class RestaurantGalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
