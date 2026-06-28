from django.urls import path
from . import views

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('sell/', views.listing_create, name='listing_create'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('seller/<str:username>/', views.seller_profile, name='seller_profile'),
    path('<int:pk>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('<int:pk>/', views.listing_detail, name='listing_detail'),
    path('<int:pk>/edit/', views.listing_edit, name='listing_edit'),
    path('<int:pk>/delete/', views.listing_delete, name='listing_delete'),
    path('<int:pk>/buy/', views.buy_listing, name='buy_listing'),
    path('<int:pk>/buy/success/', views.buy_success, name='buy_success'),
    path('<int:pk>/promote/', views.promote_listing, name='promote_listing'),
path('<int:pk>/promote/success/', views.promote_success, name='promote_success'),
]
