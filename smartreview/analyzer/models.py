from django.db import models
from django.contrib.auth.models import User

class User(models.Model):
    name = models.CharField(max_length=100, default="John Doe")
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100, default="password123")
    phone = models.CharField(max_length=15, default="1234567890")
    address = models.CharField(max_length=255, default='123 Main St, City, Country')
    city = models.CharField(max_length=100, default='City')
    state = models.CharField(max_length=100, default='State')
    country = models.CharField(max_length=100, default='Country')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50, default="Unknown Platform")  # e.g., Amazon, Flipkart
    product_name = models.CharField(max_length=255, default="Unknown Product")
    product_image = models.URLField(blank=True, null=True)
    product_url = models.URLField(null=True, blank=True)

    text = models.TextField()  # Review snippet or full text
    sentiment = models.CharField(max_length=20)  # Positive/Neutral/Negative
    keywords = models.TextField()  # Comma-separated keywords

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} ({self.sentiment})"