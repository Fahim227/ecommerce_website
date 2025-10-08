from django.db import models

from django.db import models
from django.utils.text import slugify

class Product(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    price = models.IntegerField(null=False, blank=False)
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Main image
    slug = models.SlugField(unique=True)
    discount_percentage = models.IntegerField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    review_count = models.IntegerField(blank=True, null=True)

    def discounted_price(self):
        """Return the price after discount if applicable."""
        if self.discount_percentage:
            discount_amount = (self.price * self.discount_percentage) / 100
            return int(self.price - discount_amount)
        return self.price

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Image for {self.product.title}"


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id} - {self.product.title} ({self.full_name})'