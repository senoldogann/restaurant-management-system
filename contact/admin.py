from django.contrib import admin
from django.core.mail import send_mail
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_answered')
    list_filter = ('is_answered', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Mesaj Bilgileri', {
            'fields': ('name', 'email', 'subject', 'message', 'created_at')
        }),
        ('Yanıt', {
            'fields': ('is_answered', 'answer', 'answered_by', 'answered_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('answer') and not obj.is_answered:
            try:
                # HTML e-posta şablonunu hazırla
                context = {
                    'name': obj.name,
                    'message': obj.message,
                    'answer': form.cleaned_data['answer'],
                    'site_name': settings.SITE_NAME
                }
                
                # HTML içeriğini oluştur
                html_message = render_to_string('contact/email/answer_template.html', context)
                # Düz metin versiyonunu oluştur
                plain_message = strip_tags(html_message)
                
                # E-postayı gönder
                send_mail(
                    subject=f'{settings.SITE_NAME} - İletişim Formu Yanıtı',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[obj.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                # Mesajı yanıtlandı olarak işaretle
                obj.is_answered = True
                obj.answered_by = request.user
                obj.answered_at = timezone.now()
                
                self.message_user(request, 'E-posta başarıyla gönderildi.', level=messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f'E-posta gönderilirken bir hata oluştu: {str(e)}', level=messages.ERROR)
        
        super().save_model(request, obj, form, change) 