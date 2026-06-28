from django.shortcuts import render


def listing_list(request):
    return render(request, "listings/listing_list.html")


def listing_detail(request):
    return render(request, "listings/listing_detail.html")