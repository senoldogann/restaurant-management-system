from django.core.management.base import BaseCommand
from foodanddrink.models import Cart

def fix_active_carts():
    # Tüm kullanıcılar için aktif sepetleri düzelt
    from django.contrib.auth.models import User
    for user in User.objects.all():
        active_carts = Cart.objects.filter(user=user, is_active=True)
        if active_carts.count() > 1:
            # En son sepeti aktif tut, diğerlerini deaktif yap
            latest_cart = active_carts.latest('created_at')
            active_carts.exclude(id=latest_cart.id).update(is_active=False)

class Command(BaseCommand):
    help = 'Fixes multiple active carts issue'

    def handle(self, *args, **options):
        fix_active_carts()
        self.stdout.write(self.style.SUCCESS('Successfully fixed active carts')) 