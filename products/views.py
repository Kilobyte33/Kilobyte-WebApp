from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Avg

from .models import Product, Category, Wishlist, Review
from .forms import ProductForm, ReviewForm


# ─── Public Views ────────────────────────────────────────────────────────────

def product_list(request):
    query = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    try:
        category_id = int(request.GET.get('category', 0))
    except (ValueError, TypeError):
        category_id = 0

    products = Product.objects.filter(status='active').select_related('owner', 'category')

    if query:
        products = products.filter(name__icontains=query)
    if city:
        products = products.filter(city__icontains=city)
    if category_id:
        products = products.filter(category_id=category_id)

    featured_products = Product.objects.filter(is_featured=True, status='active').order_by('-created_at')[:6]

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Wishlist ids for logged-in user
    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist_ids = set(wishlist.products.values_list('id', flat=True))

    return render(request, 'products/product_list.html', {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'featured_products': featured_products,
        'wishlist_ids': wishlist_ids,
        'query': query,
        'city': city,
        'selected_category': category_id,
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    # Increment view count
    Product.objects.filter(id=id).update(views_count=product.views_count + 1)
    product.views_count += 1

    in_wishlist = False
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        in_wishlist = wishlist.products.filter(id=id).exists()

    reviews = Review.objects.filter(seller=product.owner).select_related('reviewer').order_by('-created_at')
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    already_reviewed = False
    review_form = None

    if request.user.is_authenticated and request.user != product.owner:
        already_reviewed = reviews.filter(reviewer=request.user).exists()
        if not already_reviewed:
            review_form = ReviewForm()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'in_wishlist': in_wishlist,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'already_reviewed': already_reviewed,
        'review_form': review_form,
    })


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category, status='active').select_related('owner')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'products/category_products.html', {
        'category': category,
        'page_obj': page_obj,
        'categories': Category.objects.all(),
    })


def seller_profile(request, username):
    seller = get_object_or_404(User, username=username)
    products = Product.objects.filter(owner=seller, status='active').order_by('-created_at')
    reviews = Review.objects.filter(seller=seller).select_related('reviewer').order_by('-created_at')
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    already_reviewed = False
    review_form = None

    if request.user.is_authenticated and request.user != seller:
        already_reviewed = reviews.filter(reviewer=request.user).exists()
        if not already_reviewed:
            review_form = ReviewForm()

    return render(request, 'products/seller_profile.html', {
        'seller': seller,
        'products': products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'already_reviewed': already_reviewed,
        'review_form': review_form,
    })


# ─── Auth-Required Views ──────────────────────────────────────────────────────

@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            messages.success(request, 'Product posted successfully!')
            return redirect('product_detail', id=product.id)
    else:
        form = ProductForm()
    return render(request, 'products/create_product.html', {'form': form})


@login_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id, owner=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            saved = form.save(commit=False)
            # Only replace image if a new one was uploaded
            if not request.FILES.get('image'):
                saved.image = product.image
            saved.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_detail', id=product.id)
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id, owner=request.user)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('my_listings')

    return render(request, 'products/delete_product.html', {'product': product})


@login_required
def mark_sold(request, id):
    product = get_object_or_404(Product, id=id, owner=request.user)
    product.status = 'sold'
    product.save()
    messages.success(request, f'"{product.name}" marked as sold.')
    return redirect('my_listings')


@login_required
def my_listings(request):
    products = Product.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'products/my_listings.html', {'products': products})


@login_required
def wishlist_toggle(request, id):
    product = get_object_or_404(Product, id=id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    if wishlist.products.filter(id=product.id).exists():
        wishlist.products.remove(product)
        in_wishlist = False
    else:
        wishlist.products.add(product)
        in_wishlist = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'in_wishlist': in_wishlist})

    return redirect('product_detail', id=id)


@login_required
def wishlist_list(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.filter(status='active').order_by('-created_at')
    return render(request, 'products/wishlist.html', {'products': products})


@login_required
def leave_review(request, username):
    seller = get_object_or_404(User, username=username)

    if request.user == seller:
        messages.error(request, "You cannot review yourself.")
        return redirect('seller_profile', username=username)

    if Review.objects.filter(seller=seller, reviewer=request.user).exists():
        messages.error(request, "You have already reviewed this seller.")
        return redirect('seller_profile', username=username)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(
                seller=seller,
                reviewer=request.user,
                rating=form.cleaned_data['rating'],
                comment=form.cleaned_data['comment'],
            )
            messages.success(request, 'Review submitted!')
    return redirect('seller_profile', username=username)
