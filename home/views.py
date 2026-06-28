from django.shortcuts import render
from listings.models import Listing, Wishlist


def home(request):
    latest_listings = Listing.objects.order_by("-is_featured", "-created_at")[:6]
    saved_listing_ids = []

    if request.user.is_authenticated:
        saved_listing_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list("listing_id", flat=True)

    return render(
        request,
        "home/index.html",
        {
            "latest_listings": latest_listings,
            "saved_listing_ids": saved_listing_ids,
        },
    )
