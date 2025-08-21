from django.urls import path
from . import views

urlpatterns = [
    path("tambah/", views.tambah_simpanan, name="tambah_simpanan"),
    path("daftar/", views.daftar_simpanan, name="daftar_simpanan"),
    path("detail/<str:nomor_anggota>/", views.detail_simpanan, name="detail_simpanan"),
]

