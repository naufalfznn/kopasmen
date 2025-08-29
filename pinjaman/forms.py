from django import forms
from .models import Pinjaman, KategoriJasa, JenisPinjaman
from anggota.models import Anggota

class PinjamanForm(forms.ModelForm):
    class Meta:
        model = Pinjaman
        fields = [
            'nomor_anggota',
            'id_jenis_pinjaman',
            'id_kategori_jasa',
            'id_admin',
            'tanggal_meminjam',
            'jatuh_tempo',
            'jumlah_pinjaman',
            'angsuran_per_bulan',
            'jasa',
            'status',

        ]
        widgets = {
            'nomor_anggota': forms.Select(attrs={'class': 'form-control'}),
            'id_jenis_pinjaman': forms.Select(attrs={'class': 'form-control'}),
            'id_kategori_jasa': forms.Select(attrs={'class': 'form-control'}),
            'id_admin': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_meminjam': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'jatuh_tempo': forms.NumberInput(attrs={'class': 'form-control','min': 1,'max': 36,'placeholder': 'Masukkan jumlah bulan (1-36)'}),
            'jumlah_pinjaman': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Jumlah Pinjaman'}),
            'angsuran_per_bulan': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Jumlah Cicilan'}),
            'jasa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Jumlah Jasa'}),
            'status': forms.Select(choices=[('Lunas', 'Lunas'), ('Belum Lunas', 'Belum Lunas')],
                                   attrs={'class': 'form-control'}),
        }
