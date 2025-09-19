from django.urls import path
from . import views

urlpatterns = [
    path("tambah/", views.tambah_simpanan, name="tambah_simpanan"),
    path("daftar/", views.daftar_simpanan, name="daftar_simpanan"),
    
    # ganti <int:jenis> -> <str:jenis>
    path("penarikan/<str:nomor_anggota>/<int:jenis>/", views.tambah_penarikan, name="tambah_penarikan"),

    path("anggota/<str:nomor_anggota>/", views.simpanan_anggota, name="simpanan_anggota"),
    path('detail/<int:id_simpanan>/', views.detail_simpanan, name='detail_simpanan'),

    # Edit / hapus berdasarkan anggota
    path("edit/<str:nomor_anggota>/", views.edit_simpanan, name="edit_simpanan"),
    path("simpanan/<str:nomor_anggota>/hapus/", views.hapus_simpanan, name="hapus_simpanan"),
]
