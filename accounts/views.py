from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileForm, ZimbabweAuthenticationForm


def home(request):
    if request.user.is_authenticated:
        return redirect('product_list')
    from products.models import Category, Product

    featured_products = Product.objects.filter(status='active').select_related('category').order_by('-created_at')[:8]
    featured_categories = Category.objects.order_by('name')[:6]

    return render(request, 'accounts/home.html', {
        'featured_products': featured_products,
        'featured_categories': featured_categories,
    })


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


class ZimbabweLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = ZimbabweAuthenticationForm


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('edit_profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def my_listings(request):
    from products.models import Product
    products = Product.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'products/my_listings.html', {'products': products})
