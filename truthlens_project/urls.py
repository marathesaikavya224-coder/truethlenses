from django.contrib import admin
from django.urls import path
from analyzer import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('api/analyze/', views.analyze, name='analyze'),
    path('api/register-reference/', views.register_reference, name='register_reference'),
    path('api/references/', views.references, name='references'),
]
