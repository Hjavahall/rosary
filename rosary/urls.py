from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('register/', views.register, name='register'),
    path('active/', views.active_users, name='active_users'),
    path('stats/', views.stats_page, name='stats'),
    path('map/data/', views.prayer_heatmap_data, name='heatmap_data'),
    path('map/', views.heatmap_page, name='heatmap'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('start/', views.rosary_start, name='rosary_start'),
    path('pray/', views.rosary_intro, name='rosary_intro'),
    path('pray/flow/', views.rosary_flow, name='rosary_flow'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
