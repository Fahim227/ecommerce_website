import uuid, random, os
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Product, Category, ProductImage


class Command(BaseCommand):
    help = "Import products from local folders"

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Path to products folder')
        parser.add_argument('--category', type=str, help='Category name')

    def handle(self, *args, **options):
        base_path = options['path']

        categories = [
            "Corporate",
            "Home Appliances",
            "Kitchen & Cooking",
            "Moms & Kids",
            "Beauty & Jewellery",
            "Health & Lifestyle",
            "Electronics & Gadgets",
            "Package & Bundle"
        ]


        if not base_path or not os.path.exists(base_path):
            self.stdout.write(self.style.ERROR("Invalid path"))
            return
        
        print("base_path",base_path)
        for folder in os.listdir(base_path):
            category_name = random.choice(categories)
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={'slug': slugify(category_name)}
            )
            product_path = os.path.join(base_path, folder)
            if not os.path.isdir(product_path):
                continue

            self.stdout.write(f"Processing: {folder}")

            # Read description
            desc_file = os.path.join(product_path, "details.txt")
            description = ""
            if os.path.exists(desc_file):
                with open(desc_file, "r", encoding="utf-8") as f:
                    description = f.read().strip()

            # Find images
            images = [
                os.path.join(product_path, f)
                for f in os.listdir(product_path)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            ]
            if not images:
                self.stdout.write(self.style.WARNING(f"No images found for {folder}"))
                continue

            # Create product
            slug = slugify(folder)[:120]
            productJson = {
                    "title": folder,
                    "short_description": description[:250],
                    "description": description,
                    "price": 1300,  # You can set manually or read from somewhere
                    "category": category,
                    
                }
            print("Not empty Image ===",images.count != 0)
            if(images.count != 0):
                with open(images[0], "rb") as img_file:
                    productJson["image"] =  File(img_file, name=os.path.basename(images[0]))
                    print(productJson["image"] )
                    product, created = Product.objects.get_or_create(
                            slug=slug,
                        defaults=productJson
                    )
            # try:
            # product, created = Product.objects.get_or_create(
            #     slug=slug,
            #     defaults=productJson
            # )
            # except:

            #     del productJson["image"]
            #     product, created = Product.objects.get_or_create(
            #     slug=slug,
            #     defaults=productJson
            # )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {folder}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated: {folder}"))

            # Add images
            for image_path in images:
                with open(image_path, "rb") as img_file:
                    ProductImage.objects.create(
                        product=product,
                        image=File(img_file, name=os.path.basename(image_path))
                    )

        self.stdout.write(self.style.SUCCESS("✅ Product import completed!"))
