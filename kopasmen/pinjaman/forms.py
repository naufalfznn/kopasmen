from django import forms
from .models import Pinjaman, Anggota, JenisPinjaman

class PinjamanForm(forms.ModelForm):
    class Meta:
        model = Pinjaman
        fields = [
            'nomor_anggota', 
            'id_jenis_pinjaman', 
            'jumlah_pinjaman', 
            'angsuran_per_bulan', 
            'jasa', 
            'tanggal_meminjam', 
            'jatuh_tempo', 
            'status'
        ]
        
    def clean_jumlah_pinjaman(self):
        jumlah_pinjaman = self.cleaned_data.get('jumlah_pinjaman')
        if jumlah_pinjaman <= 0:
            raise forms.ValidationError("Jumlah pinjaman harus lebih besar dari 0.")
        return jumlah_pinjaman

    def clean_angsuran_per_bulan(self):
        angsuran_per_bulan = self.cleaned_data.get('angsuran_per_bulan')
        if angsuran_per_bulan <= 0:
            raise forms.ValidationError("Angsuran per bulan harus lebih besar dari 0.")
        return angsuran_per_bulan
