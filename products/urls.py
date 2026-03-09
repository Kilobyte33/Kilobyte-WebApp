from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('create/', views.create_product, name='create_product'),
    path('<int:id>/', views.product_detail, name='product_detail'),
    path('<int:id>/edit/', views.edit_product, name='edit_product'),
    path('<int:id>/delete/', views.delete_product, name='delete_product'),
    path('<int:id>/sold/', views.mark_sold, name='mark_sold'),
    path('wishlist/', views.wishlist_list, name='wishlist_list'),
    path('wishlist/<int:id>/toggle/', views.wishlist_toggle, name='wishlist_toggle'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('seller/<str:username>/', views.seller_profile, name='seller_profile'),
    path('seller/<str:username>/review/', views.leave_review, name='leave_review'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
]