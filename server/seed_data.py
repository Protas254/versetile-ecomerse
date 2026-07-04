import os
import django
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Product, Review
from django.contrib.auth.models import User

def seed_data():
    # 1. Create Superuser if not exists
    if not User.objects.filter(username='Protas').exists():
        User.objects.create_superuser('Protas', 'protasjunior254@gmail.com', 'Protas@01')
        print("Superuser 'Protas' created.")

    # 2. Add Products
    products_data = [
        {
            "name": "Rose Éternelle",
            "price": 12500.00,
            "description": "A timeless floral masterpiece featuring Hand-picked Damask roses blended with white musk and delicate peony. Perfect for romantic evenings and sophisticated occasions.",
            "scent_type": "Floral",
            "stock": 15,
            "featured": True,
            "image": "products/floral_perfume.png",
            "fragrance_notes": {
                "top": ["Bergamot", "Pink Pepper", "Peony"],
                "middle": ["Damask Rose", "Jasmine", "Lily"],
                "base": ["White Musk", "Cedarwood", "Patchouli"]
            }
        },
        {
            "name": "Ambre Noir",
            "price": 14200.00,
            "description": "A deep, mysterious fragrance that combines rich amber with smoky sandalwood and spiced cardamom. A bold choice for the modern gentleman.",
            "scent_type": "Woody",
            "stock": 8,
            "featured": True,
            "image": "products/woody_perfume.png",
            "fragrance_notes": {
                "top": ["Cardamom", "Citrus", "Sage"],
                "middle": ["Sandalwood", "Spices", "Leather"],
                "base": ["Amber", "Tonka Bean", "Vetiver"]
            }
        },
        {
            "name": "Aqua Crystal",
            "price": 9800.00,
            "description": "Crisp and refreshing, Aqua Crystal evokes the purity of a morning breeze over the ocean. Light, airy, and invigorating.",
            "scent_type": "Fresh",
            "stock": 25,
            "featured": True,
            "image": "products/fresh_perfume.png",
            "fragrance_notes": {
                "top": ["Sea Salt", "Lemon", "Mint"],
                "middle": ["Water Lily", "Seaweed", "Cucumber"],
                "base": ["Silver Musk", "Driftwood", "Ambergris"]
            }
        },
        {
            "name": "Mystique Orient",
            "price": 18500.00,
            "description": "An opulent blend of rare Oud, warm vanilla, and exotic spices from the silk road. Intense, rich, and unforgettable.",
            "scent_type": "Oriental",
            "stock": 5,
            "featured": True,
            "image": "products/oriental_perfume.png",
            "fragrance_notes": {
                "top": ["Saffron", "Oud", "Incense"],
                "middle": ["Rose", "Labdanum", "Caramel"],
                "base": ["Vanilla", "Agarwood", "Leather"]
            }
        }
    ]

    for p_data in products_data:
        product, created = Product.objects.get_or_create(
            name=p_data['name'],
            defaults={
                'price': p_data['price'],
                'description': p_data['description'],
                'scent_type': p_data['scent_type'],
                'stock': p_data['stock'],
                'featured': p_data['featured'],
                'image': p_data['image'],
                'fragrance_notes': p_data['fragrance_notes']
            }
        )
        if created:
            print(f"Product '{product.name}' created.")
        else:
            print(f"Product '{product.name}' already exists.")

if __name__ == '__main__':
    seed_data()
