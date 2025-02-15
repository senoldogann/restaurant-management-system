# Generated by Django 5.0.1 on 2025-02-15 16:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodanddrink', '0006_contactmessage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='contactmessage',
            name='answer',
            field=models.TextField(blank=True, null=True, verbose_name='Yanıt'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='answered_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Yanıt Tarihi'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='answered_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='answered_messages', to=settings.AUTH_USER_MODEL, verbose_name='Yanıtlayan'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='is_answered',
            field=models.BooleanField(default=False, verbose_name='Yanıtlandı mı?'),
        ),
    ]
