from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.core.validators import MinValueValidator


# CUSTOM USER MANAGER
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not first_name:
            raise ValueError("First name is required")

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        
        # We don't store passwords since Supabase handles authentication
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name=None, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self.create_user(email, first_name, last_name, password, **extra_fields)


# CUSTOM USER MODEL
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)  # Fix here
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return self.email



#  PRODUCT MODEL
class Product(models.Model):
    asin = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=500)  # Increased length for title
    image_url = models.URLField()
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    rating = models.CharField(max_length=20, default="0 out of 5 stars")
    stock_status = models.CharField(max_length=255, blank=True, null=True)
    amazon_url = models.URLField(max_length=1000)  # Increased length for amazon_url



    def __str__(self):
        return self.title

# TRACKED PRODUCT MODEL
class TrackedProduct(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    target_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.01)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_user_product_tracking")
        ]

    def __str__(self):
        return f"{self.user.email} tracking {self.product.title} at {self.target_price}"
    
from .models import Product, CustomUser


class PriceHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Keep if tracking per user
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_history")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.product.title} - ₹{self.price} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    


class Bestseller(models.Model):
    title = models.CharField(max_length=500)  # Increase from 200 to 500
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image_url = models.URLField()
    product_url = models.URLField(unique=True, max_length=1000)  # Increase from 200 to 1000
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TodayDeals(models.Model):
    title = models.CharField(max_length=500)  # Increase from 200 to 500
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image_url = models.URLField()
    product_url = models.URLField(unique=True, max_length=1000)  # Increase from 200 to 1000
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

