# Generated by Django 5.1.6 on 2025-02-12 20:48

import ckeditor.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BarInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Bar Adı')),
                ('logo', models.ImageField(upload_to='bar/logos/', verbose_name='Logo')),
                ('description', ckeditor.fields.RichTextField(verbose_name='Açıklama')),
                ('address', models.TextField(verbose_name='Adres')),
                ('phone', models.CharField(max_length=20, verbose_name='Telefon')),
                ('email', models.EmailField(max_length=254, verbose_name='E-posta')),
                ('opening_hours', models.CharField(max_length=100, verbose_name='Çalışma Saatleri')),
            ],
            options={
                'verbose_name': 'Bar Bilgisi',
                'verbose_name_plural': 'Bar Bilgileri',
            },
        ),
        migrations.CreateModel(
            name='DrinkCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Kategori Adı')),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('image', models.ImageField(upload_to='bar/categories/', verbose_name='Kategori Görseli')),
                ('description', models.TextField(blank=True, verbose_name='Açıklama')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktif mi?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'İçecek Kategorisi',
                'verbose_name_plural': 'İçecek Kategorileri',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Etkinlik Başlığı')),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', ckeditor.fields.RichTextField(verbose_name='Açıklama')),
                ('image', models.ImageField(upload_to='bar/events/', verbose_name='Etkinlik Görseli')),
                ('date', models.DateField(verbose_name='Tarih')),
                ('time', models.TimeField(verbose_name='Saat')),
                ('location', models.CharField(max_length=200, verbose_name='Konum')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Bilet Fiyatı')),
                ('capacity', models.PositiveIntegerField(blank=True, null=True, verbose_name='Kapasite')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktif mi?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Etkinlik',
                'verbose_name_plural': 'Etkinlikler',
                'ordering': ['date', 'time'],
            },
        ),
        migrations.CreateModel(
            name='Drink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='İçecek Adı')),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', ckeditor.fields.RichTextField(verbose_name='Açıklama')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Fiyat')),
                ('image', models.ImageField(upload_to='bar/drinks/', verbose_name='İçecek Görseli')),
                ('ingredients', models.TextField(verbose_name='İçindekiler')),
                ('is_available', models.BooleanField(default=True, verbose_name='Mevcut mu?')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Öne Çıkan')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drinks', to='bar.drinkcategory', verbose_name='Kategori')),
            ],
            options={
                'verbose_name': 'İçecek',
                'verbose_name_plural': 'İçecekler',
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Ad Soyad')),
                ('email', models.EmailField(max_length=254, verbose_name='E-posta')),
                ('phone', models.CharField(max_length=20, verbose_name='Telefon')),
                ('date', models.DateField(verbose_name='Tarih')),
                ('time', models.TimeField(verbose_name='Saat')),
                ('guests', models.PositiveIntegerField(verbose_name='Kişi Sayısı')),
                ('notes', models.TextField(blank=True, verbose_name='Notlar')),
                ('status', models.CharField(choices=[('pending', 'Beklemede'), ('confirmed', 'Onaylandı'), ('cancelled', 'İptal Edildi')], default='pending', max_length=20, verbose_name='Durum')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reservations', to='bar.event', verbose_name='Etkinlik')),
            ],
            options={
                'verbose_name': 'Rezervasyon',
                'verbose_name_plural': 'Rezervasyonlar',
                'ordering': ['-created_at'],
            },
        ),
    ]
