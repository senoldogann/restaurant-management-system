# Generated by Django 5.0.1 on 2025-02-15 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0007_alter_menuitem_allergens_alter_menuitem_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='allergens',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='Alerjenler'),
        ),
    ]
