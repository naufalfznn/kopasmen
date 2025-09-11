from django import forms
from .models import Simpanan, Admin, Anggota

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

class EditSimpananForm(forms.Form):
    anggota = forms.ModelChoiceField(
        queryset=Anggota.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    admin = forms.ModelChoiceField(
        queryset=Admin.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tanggal_menyimpan = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    simpanan_pokok = forms.IntegerField(
        required=False, widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    simpanan_wajib = forms.IntegerField(
        required=False, widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    simpanan_sukarela = forms.IntegerField(
        required=False, widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['anggota'].queryset = Anggota.objects.all()
        self.fields['admin'].queryset = Admin.objects.all()
