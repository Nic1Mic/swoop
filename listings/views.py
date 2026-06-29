from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ListingForm
from .models import Category, Listing, Wishlist

import stripe
from django.conf import settings


def listing_list(request):
    query = request.GET.get("q", "")
    category_slug = request.GET.get("category", "")
    condition = request.GET.get("condition", "")
    max_price = request.GET.get("max_price", "")
    sort = request.GET.get("sort", "featured")

    listings = Listing.objects.all()
    categories = Category.objects.all()
    saved_listing_ids = []

    if request.user.is_authenticated:
        saved_listing_ids = Wishlist.objects.filter(user=request.user).values_list("listing_id", flat=True)

    if query:
        listings = listings.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )

    if category_slug:
        listings = listings.filter(category__slug=category_slug)

    if condition:
        listings = listings.filter(condition=condition)

    if max_price:
        listings = listings.filter(price__lte=max_price)

    if sort == "newest":
        listings = listings.order_by("-created_at")
    elif sort == "price_low":
        listings = listings.order_by("price")
    elif sort == "price_high":
        listings = listings.order_by("-price")
    else:
        listings = listings.order_by("-is_featured", "-created_at")

    paginator = Paginator(listings, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "listings/listing_list.html",
        {
            "listings": page_obj,
            "page_obj": page_obj,
            "categories": categories,
            "query": query,
            "category_slug": category_slug,
            "condition": condition,
            "max_price": max_price,
            "sort": sort,
            "saved_listing_ids": saved_listing_ids,
        },
    )

def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    return render(request, "listings/listing_detail.html", {"listing": listing})


@login_required
def listing_create(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)

        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            return redirect("dashboard")
    else:
        form = ListingForm()

    return render(request, "listings/listing_form.html", {"form": form, "page_title": "Sell an item on Swoop."})


@login_required
def listing_edit(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)

    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES, instance=listing)

        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ListingForm(instance=listing)

    return render(request, "listings/listing_form.html", {"form": form, "page_title": "Edit your listing."})


@login_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)

    if request.method == "POST":
        listing.delete()
        return redirect("dashboard")

    return render(request, "listings/listing_confirm_delete.html", {"listing": listing})


@login_required
def dashboard(request):
    my_listings = Listing.objects.filter(seller=request.user)
    sold_count = my_listings.filter(is_sold=True).count()
    featured_count = my_listings.filter(is_featured=True).count()

    return render(
        request,
        "listings/dashboard.html",
        {
            "my_listings": my_listings,
            "sold_count": sold_count,
            "featured_count": featured_count,
        },
    )


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related("listing")
    return render(request, "listings/wishlist.html", {"wishlist_items": wishlist_items})


@login_required
def toggle_wishlist(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    item, created = Wishlist.objects.get_or_create(
        user=request.user,
        listing=listing,
    )

    if not created:
        item.delete()

    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or "listing_list"
    return redirect(next_url)


def seller_profile(request, username):
    from django.contrib.auth.models import User

    seller = get_object_or_404(User, username=username)
    seller_listings = Listing.objects.filter(seller=seller)
    active_listings = seller_listings.filter(is_sold=False)
    sold_count = seller_listings.filter(is_sold=True).count()
    featured_count = seller_listings.filter(is_featured=True).count()

    return render(
        request,
        "listings/seller_profile.html",
        {
            "seller": seller,
            "seller_listings": active_listings,
            "total_count": seller_listings.count(),
            "sold_count": sold_count,
            "featured_count": featured_count,
        },
    )

@login_required
def promote_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "unit_amount": settings.PROMOTE_PRICE,
                    "product_data": {
                        "name": f"Promote listing: {listing.title}",
                    },
                },
                "quantity": 1,
            }
        ],
        success_url=f"{settings.SITE_URL}/listings/{listing.id}/promote/success/",
        cancel_url=f"{settings.SITE_URL}/listings/dashboard/",
    )

    return redirect(checkout_session.url)


@login_required
def promote_success(request, pk):
    from django.core.mail import send_mail

    listing = get_object_or_404(Listing, pk=pk, seller=request.user)
    listing.is_featured = True
    listing.save()

    if request.user.email:
        send_mail(
            subject="Your Swoop listing is now featured",
            message=f"Hi {request.user.username},\n\nYour listing '{listing.title}' has been successfully promoted and is now featured on Swoop.\n\nThanks for using Swoop!",
            from_email=None,
            recipient_list=[request.user.email],
            fail_silently=False,
        )

    return render(request, "listings/promote_success.html", {"listing": listing})

@login_required
def buy_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if listing.seller == request.user:
        return redirect("listing_detail", pk=listing.id)

    if listing.is_sold:
        return redirect("listing_detail", pk=listing.id)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "unit_amount": int(listing.price * 100),
                    "product_data": {
                        "name": listing.title,
                    },
                },
                "quantity": 1,
            }
        ],
        success_url=f"{settings.SITE_URL}/listings/{listing.id}/buy/success/",
        cancel_url=f"{settings.SITE_URL}/listings/{listing.id}/",
    )

    return redirect(checkout_session.url)


@login_required
def buy_success(request, pk):
    from django.core.mail import send_mail

    listing = get_object_or_404(Listing, pk=pk)

    if listing.seller != request.user:
        listing.is_sold = True
        listing.save()

        if request.user.email:
            send_mail(
                subject="Your Swoop purchase confirmation",
                message=f"Hi {request.user.username},\n\nYou successfully purchased '{listing.title}' for £{listing.price}.\n\nThanks for using Swoop!",
                from_email=None,
                recipient_list=[request.user.email],
                fail_silently=True,
            )

        if listing.seller.email:
            send_mail(
                subject="Your item sold on Swoop",
                message=f"Hi {listing.seller.username},\n\nYour listing '{listing.title}' has been sold for £{listing.price}.\n\nBuyer: {request.user.username}\n\nPlease arrange the next steps with the buyer.",
                from_email=None,
                recipient_list=[listing.seller.email],
                fail_silently=True,
            )

    return render(request, "listings/buy_success.html", {"listing": listing})