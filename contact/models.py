from django.db import models
from django.conf import settings

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name='İsim')
    email = models.EmailField(verbose_name='E-posta')
    subject = models.CharField(max_length=200, verbose_name='Konu')
    message = models.TextField(verbose_name='Mesaj')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Gönderim Tarihi')
    is_answered = models.BooleanField(default=False, verbose_name='Yanıtlandı')
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='answered_messages',
        verbose_name='Yanıtlayan'
    )
    answer = models.TextField(blank=True, null=True, verbose_name='Yanıt')
    answered_at = models.DateTimeField(null=True, blank=True, verbose_name='Yanıt Tarihi')

    class Meta:
        verbose_name = 'İletişim Mesajı'
        verbose_name_plural = 'İletişim Mesajları'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}" 