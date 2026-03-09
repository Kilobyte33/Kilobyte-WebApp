from django.contrib import admin
from .models import Product, Category, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'city', 'status', 'is_featured', 'is_wholesale', 'views_count', 'created_at')
    list_editable = ('is_featured', 'status')
    list_filter = ('category', 'status', 'is_featured', 'is_wholesale')
    search_fields = ('name', 'description', 'city', 'owner__username')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'seller', 'rating', 'created_at')
