from django.urls import path
from . import views

urlpatterns = [
    path('', views.pinjaman_list, name='pinjaman_list'),
    path('tambah/', views.tambah_pinjaman, name='tambah_pinjaman'),
]
