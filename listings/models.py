from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Listing(models.Model):
    CONDITION_CHOICES = [
        ("new", "New"),
        ("like_new", "Like new"),
        ("good", "Good"),
        ("used", "Used"),
    ]

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="listings")
    title = models.CharField(max_length=120)
    description = models.TextField(max_length=500)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    location = models.CharField(max_length=120)
    image = models.ImageField(upload_to="listings/", blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("listing_detail", args=[self.id])


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="listings/")
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.listing.title} image"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "listing")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} saved {self.listing.title}"
