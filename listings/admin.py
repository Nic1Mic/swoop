from django.contrib import admin
from .models import Category, Listing, ListingImage


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "seller",
        "category",
        "price",
        "condition",
        "is_featured",
        "is_sold",
    )

    list_filter = (
        "category",
        "condition",
        "is_featured",
        "is_sold",
    )

    search_fields = (
        "title",
        "description",
    )

    inlines = [ListingImageInline]