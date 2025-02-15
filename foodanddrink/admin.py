from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import HomePageSettings, UserProfile, Review, ReviewResponse, ContactMessage
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings

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

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read', 'is_answered')
    list_filter = ('is_read', 'is_answered', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'answered_by', 'answered_at')
    
    fieldsets = (
        ('Mesaj Bilgileri', {
            'fields': ('name', 'email', 'subject', 'message', 'created_at', 'is_read')
        }),
        ('Yanıt', {
            'fields': ('is_answered', 'answer', 'answered_by', 'answered_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if 'answer' in form.changed_data and obj.answer:
            obj.is_answered = True
            obj.answered_by = request.user
            obj.answered_at = timezone.now()
            
            # E-posta şablonunu hazırla
            context = {
                'name': obj.name,
                'message': obj.message,
                'answer': obj.answer,
                'site_name': settings.SITE_NAME
            }
            
            html_message = render_to_string('contact/email/answer_template.html', context)
            plain_message = strip_tags(html_message)
            
            print(f"Debug - Mail gönderiliyor:")
            print(f"Alıcı: {obj.email}")
            print(f"Konu: Re: {obj.subject}")
            print(f"İçerik: {plain_message}")
            
            # E-postayı gönder
            try:
                send_mail(
                    subject=f'Re: {obj.subject}',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[obj.email],
                    html_message=html_message
                )
                print("Mail başarıyla gönderildi!")
            except Exception as e:
                print(f"Mail gönderimi sırasında hata: {str(e)}")
                self.message_user(request, f"E-posta gönderilirken bir hata oluştu: {str(e)}", level='ERROR')
            else:
                self.message_user(request, "Yanıt başarıyla gönderildi.", level='SUCCESS')
        
        super().save_model(request, obj, form, change)

# Varsayılan User admin'i özelleştirilmiş versiyonla değiştir
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin) 