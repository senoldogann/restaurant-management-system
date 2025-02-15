# Generated by Django 5.0.1 on 2025-02-15 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodanddrink', '0005_reviewresponse_is_edited_reviewresponse_updated_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Ad Soyad')),
                ('email', models.EmailField(max_length=254, verbose_name='E-posta')),
                ('subject', models.CharField(max_length=200, verbose_name='Konu')),
                ('message', models.TextField(verbose_name='Mesaj')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Gönderim Tarihi')),
                ('is_read', models.BooleanField(default=False, verbose_name='Okundu mu?')),
            ],
            options={
                'verbose_name': 'İletişim Mesajı',
                'verbose_name_plural': 'İletişim Mesajları',
                'ordering': ['-created_at'],
            },
        ),
    ]
