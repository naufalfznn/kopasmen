from django.urls import path
from . import views

urlpatterns = [
    path("tambah/", views.tambah_simpanan, name="tambah_simpanan"),
    path("daftar/", views.daftar_simpanan, name="daftar_simpanan"),
    path("detail/<str:nomor_anggota>/", views.detail_simpanan, name="detail_simpanan"),
    path("edit/<str:nomor_anggota>/", views.edit_simpanan, name="edit_simpanan"),
    path('<str:nomor_anggota>/hapus/', views.hapus_simpanan, name='hapus_simpanan'),

]

