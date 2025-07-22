from unicodedata import name
from django.urls import path, include, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.static import serve


# from . --> same directory
# Views functions and urls must be linked. # of views == # of urls
# App URL file - urls related to healthcenter


urlpatterns = [
    path('product-single/<int:pk>/', views.inventory_single_product, name='product-single'),
    path('inventory-view-equipment/<int:pk>/', views.inventory_view_equipment, name='inventory-view-equipment'),
    path('inventory-view-supply/<int:pk>/', views.inventory_view_supply, name='inventory-view-supply'),
    path('inventory/', views.inventory, name='inventory'),
]
    


urlpatterns += [ re_path(r'^static/images/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
