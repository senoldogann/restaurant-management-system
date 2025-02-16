from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import HomePageSettings, UserProfile, ContactMessage, Payment, Campaign, Order, OrderItem, Cart, CartItem
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

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'status', 'stripe_payment_intent_id', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('user__username', 'user__email', 'stripe_payment_intent_id')
    readonly_fields = ('stripe_payment_intent_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percentage', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'total_amount', 'created_at')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item', 'drink', 'quantity', 'price', 'total_price')

# Varsayılan User admin'i özelleştirilmiş versiyonla değiştir
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin) 