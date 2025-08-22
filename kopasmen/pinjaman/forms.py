from django import forms
from .models import Pinjaman, Anggota, JenisPinjaman

class PinjamanForm(forms.ModelForm):
    class Meta:
        model = Pinjaman
        fields = [
            'nomor_anggota',
            'id_jenis_pinjaman',
            'jumlah_pinjaman',
            'lama_peminjaman',
            'angsuran_per_bulan',
            'kategori_jasa',
            'jasa_persen',
            'jasa_pinjam',
            'tanggal_meminjam',
            'jatuh_tempo',
            'status',
            'id_admin'
        ]
        labels = {
            'nomor_anggota': 'Nomor Anggota',
            'id_jenis_pinjaman': 'Jenis Pinjaman',
            'jumlah_pinjaman': 'Jumlah Pinjaman',
            'angsuran_per_bulan': 'Angsuran',
            'lama_peminjaman': 'Lama Pinjaman',
            'kategori_jasa': 'Kategori Jasa',
            'jasa_persen' : 'Persentase Jasa', 
            'jasa_pinjam' : 'Jasa Pinjaman',
            'tanggal_meminjam': 'Tanggal Pinjam',
            'jatuh_tempo': 'Jatuh Tempo',
            'status': 'Status Pembayaran',
            'id_admin': 'Admin'
        }
        widgets = {
            'jasa_pinjam': forms.NumberInput(attrs={'step': '0.01'}),
            'tanggal_meminjam': forms.DateInput(
                format='%d-%m-%y',
                attrs={'type': 'date'}
            ),
            'jatuh_tempo': forms.DateInput(
                format='%d-%m-%y',
                attrs={'type': 'date'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Mendapatkan data dari form
        jumlah = cleaned_data.get('jumlah_pinjaman')
        jenis = cleaned_data.get('id_jenis_pinjaman')
        id_admin = cleaned_data.get('id_admin')


        if not jenis:
            raise forms.ValidationError("Jenis pinjaman harus dipilih.")
        
        if not id_admin:
            raise forms.ValidationError("Admin harus dipilih.")

        if jumlah and jenis:
            jasa_percent = jenis.jasa
            cleaned_data['jasa_pinjam'] = (jumlah * jasa_percent) / 100

        return cleaned_data
  
    def clean_jumlah_pinjaman(self):
        jumlah_pinjaman = self.cleaned_data.get('jumlah_pinjaman')
        if jumlah_pinjaman <= 0:
            raise forms.ValidationError("Jumlah pinjaman harus lebih besar dari 0.")
        return jumlah_pinjaman

    def clean_angsuran_per_bulan(self):
        angsuran_per_bulan = self.cleaned_data.get('angsuran_per_bulan')
        if angsuran_per_bulan is None or angsuran_per_bulan <= 0:
            raise forms.ValidationError("Angsuran per bulan harus lebih besar dari 0.")
        return angsuran_per_bulan
