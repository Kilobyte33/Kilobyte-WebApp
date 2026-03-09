from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='accounts_home'),
    path('signup/', views.signup, name='signup'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('my_listings/', views.my_listings, name='my_listings'),
]
