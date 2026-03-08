from django.contrib import admin
from django.urls import path, include
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # 👈 homepage
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # <- ISSO JÁ IMPORTA TODAS views do core.urls
]
