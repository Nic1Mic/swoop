from django.urls import path
from . import views

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('macbook-air-m2/', views.listing_detail, name='listing_detail'),
]