from django import forms
from .models import Simpanan

class SimpananForm(forms.ModelForm):
    class Meta:
        model = Simpanan
        fields = ['anggota', 'admin', 'jenis_simpanan', 'tanggal_menyimpan', 'jumlah_menyimpan']
        widgets = {
            'anggota': forms.Select(attrs={'class': 'form-control'}),
            'admin': forms.Select(attrs={'class': 'form-control'}),
            'jenis_simpanan': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_menyimpan': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'jumlah_menyimpan': forms.NumberInput(attrs={'class': 'form-control'}),
        }
