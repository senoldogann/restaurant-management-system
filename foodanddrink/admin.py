from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import HomePageSettings, UserProfile, Review, ReviewResponse

@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Sadece bir kayıt olmasını sağla
        return not HomePageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Silme işlemini engelle
        return False 

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Kullanıcı Profili'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')

class ReviewResponseInline(admin.TabularInline):
    model = ReviewResponse
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'location', 'user', 'rating', 'created_at', 'is_approved')
    list_filter = ('location', 'rating', 'is_approved', 'created_at')
    search_fields = ('item_name', 'user__username', 'comment')
    readonly_fields = ('created_at',)
    inlines = [ReviewResponseInline]
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Seçili değerlendirmeleri onayla"

@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ('review', 'responded_by', 'created_at')
    list_filter = ('created_at', 'responded_by')
    search_fields = ('review__item_name', 'response_text', 'responded_by__username')
    readonly_fields = ('created_at',)

# Varsayılan User admin'i özelleştirilmiş versiyonla değiştir
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin) 