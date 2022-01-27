from django.urls import path

from . import views


app_name = 'webscraper'
urlpatterns = [
    path('', views.index,name='index'),
    path('search/', views.search, name='search'),
    path('search-items/', views.webscraper, name='search_items'),
]