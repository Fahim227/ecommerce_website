import uuid
from django.db import models
from django.utils.text import slugify

class StoreConfig(models.Model):
    store_name = models.CharField(max_length=255, default="My Shop")
    logo = models.ImageField(upload_to='branding/', null=True, blank=True)
    favicon = models.ImageField(upload_to='branding/', null=True, blank=True)
    
    primary_color = models.CharField(max_length=20, default="#FF5722")   # Example
    secondary_color = models.CharField(max_length=20, default="#FFC107")
    
    theme_mode = models.CharField(
        max_length=10,
        choices=[("light", "Light"), ("dark", "Dark")],
        default="light"
    )

    # Ensure only 1 row exists
    def save(self, *args, **kwargs):
        self.pk = 1
        super(StoreConfig, self).save(*args, **kwargs)

    def __str__(self):
        return "Store Configuration"




class Category(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True,auto_created=True)  # Unique ID
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True,auto_created=True)  # Unique ID
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    description = models.TextField(blank=True)
    price = models.IntegerField(null=False, blank=False)
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Main image
    slug = models.SlugField(max_length=255,unique=True)
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
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True,auto_created=True)  
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Image for {self.product.title}"
    

class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True,auto_created=True)  
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    district = models.CharField(max_length=55)
    address = models.TextField()
    shipping_charge = models.IntegerField()
    subtotal = models.IntegerField()
    total = models.IntegerField()
    payment_method = models.CharField(max_length=20, default="COD")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"


class OrderItem(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True,auto_created=True)  
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity