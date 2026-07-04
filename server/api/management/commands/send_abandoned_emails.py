from django.core.management.base import BaseCommand
from api.utils import send_abandoned_cart_emails

class Command(BaseCommand):
    help = 'Sends recovery emails to users with abandoned carts'

    def handle(self, *args, **options):
        self.stdout.write('Checking for abandoned carts...')
        count = send_abandoned_cart_emails()
        self.stdout.write(self.style.SUCCESS(f'Successfully sent {count} recovery emails'))
