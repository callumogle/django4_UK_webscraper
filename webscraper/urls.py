from django.urls import path

from . import views


app_name = 'webscraper'
urlpatterns = [
    path('', views.IndexView.as_view(),name='index'),
    path('search/', views.search, name='search'),
    path('search-items/', views.webscraper, name='search_items'),
    path('item/<int:pk>', views.ItemDetailView.as_view(), name='item_detail'),
]