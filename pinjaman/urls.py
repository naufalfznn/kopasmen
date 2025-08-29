from django.urls import path
from . import views

urlpatterns = [
    path('', views.pinjaman_list, name='pinjaman_list'),
    path('pinjaman_anggota/', views.pinjaman_anggota, name='pinjaman_anggota'),
    path('tambah/', views.tambah_pinjaman, name='tambah_pinjaman'),
    path('detail/<int:id_pinjaman>/', views.detail_pinjaman, name='detail_pinjaman'),
    path('bayar/<int:id_pinjaman>/', views.bayar_pinjaman, name='bayar_pinjaman'),
]
