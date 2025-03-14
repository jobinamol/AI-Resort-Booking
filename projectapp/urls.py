from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('resort/', views.resortindex, name='resortindex'),
    path('guest/', views.guestindex, name='guestindex'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('blog-single/', views.blog_single, name='blog_single'),
    path('contact/', views.contact, name='contact'),
    path('main/', views.main, name='main'),
    path('restaurant/', views.restaurants, name='restaurants'),
    path('rooms/', views.rooms, name='rooms'),
    path('rooms-single/', views.rooms_single, name='rooms_single'),
    
    # Authentication URLs
    path('accounts/signup/', views.user_signup, name='user_signup'),
    path('accounts/login/', views.user_login, name='user_login'),
    path('accounts/logout/', views.user_logout, name='user_logout'),
    path('resort-dashboard/', views.ResortDashboard, name='ResortDashboard'),
]
