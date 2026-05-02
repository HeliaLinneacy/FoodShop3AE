import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'snack_shop.settings')
django.setup()

from products.models import Category, Snack
from accounts.models import User

def populate():
    # Categories
    cat1, _ = Category.objects.get_or_create(name='Chips & Crisps', description='Crunchy potato and corn snacks')
    cat2, _ = Category.objects.get_or_create(name='Sweet Treats', description='Candies, chocolates, and cookies')
    cat3, _ = Category.objects.get_or_create(name='Healthy Snacks', description='Nuts, dried fruits, and granola')

    # Snacks
    snacks_data = [
        {'category': cat1, 'snackName': 'Spicy Doritos', 'price': 2.50, 'quantity': 50, 'description': 'Spicy and crunchy corn chips.'},
        {'category': cat1, 'snackName': 'Lays Classic', 'price': 2.00, 'quantity': 100, 'description': 'Classic salted potato chips.'},
        {'category': cat1, 'snackName': 'Pringles Sour Cream', 'price': 3.00, 'quantity': 30, 'description': 'Sour cream and onion flavored crisps.'},
        {'category': cat2, 'snackName': 'Oreo Cookies', 'price': 1.50, 'quantity': 80, 'description': 'Chocolate sandwich cookies with vanilla cream.'},
        {'category': cat2, 'snackName': 'M&Ms Peanut', 'price': 1.80, 'quantity': 60, 'description': 'Peanuts coated in milk chocolate and a colorful candy shell.'},
        {'category': cat2, 'snackName': 'Snickers Bar', 'price': 1.20, 'quantity': 120, 'description': 'Chocolate bar with nougat, caramel, and peanuts.'},
        {'category': cat3, 'snackName': 'Mixed Nuts', 'price': 5.00, 'quantity': 40, 'description': 'A healthy mix of almonds, walnuts, and cashews.'},
        {'category': cat3, 'snackName': 'Dried Mango', 'price': 4.50, 'quantity': 25, 'description': 'Sweet and chewy dried mango slices.'},
        {'category': cat3, 'snackName': 'Granola Bar', 'price': 1.00, 'quantity': 200, 'description': 'Oats and honey chewy granola bar.'},
        {'category': cat1, 'snackName': 'Cheetos Flamin Hot', 'price': 2.80, 'quantity': 45, 'description': 'Dangerously cheesy and spicy snacks.'},
    ]

    for data in snacks_data:
        Snack.objects.get_or_create(snackName=data['snackName'], defaults=data)

    print("Successfully populated database with sample data!")

if __name__ == '__main__':
    populate()
