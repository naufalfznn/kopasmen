from django import forms
from django.contrib.auth.hashers import make_password
from admin_koperasi.models import Admin 
from .models import Anggota


class AdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['username', 'password_hash', 'role']
        labels = {
            'password_hash': 'Password',
        }
        widgets = {
            'password_hash': forms.PasswordInput(),
        }

    def save(self, commit=True):
        admin = super().save(commit=False)
        # kalau password belum di-hash, langsung hash
        if self.cleaned_data.get('password_hash') and not admin.password_hash.startswith('pbkdf2_sha256$'):
            admin.password_hash = make_password(self.cleaned_data['password_hash'])
        if commit:
            admin.save()
        return admin


class AnggotaForm(forms.ModelForm):
    tanggal_daftar = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}) 
    )

    class Meta:
        model = Anggota
        fields = '__all__'
        labels = {
            'nomor_anggota': 'No. Anggota',
            'nama': 'Nama',
            'nip': 'Nomor Induk Pegawai (NIP)',
            'alamat': 'Alamat',
            'no_telp': 'No. Telepon',
            'email': 'Email',
            'jenis_kelamin': 'Jenis Kelamin',
            'tanggal_daftar': 'Tanggal Daftar',
            'status': 'Status',
            'password_hash': 'Password',
        }
        widgets = {
            'password_hash': forms.PasswordInput(render_value=True),
        }

    def save(self, commit=True):
        anggota = super().save(commit=False)
        # kalau ada input password baru & belum di-hash, hash dulu
        if self.cleaned_data.get('password_hash') and not anggota.password_hash.startswith('pbkdf2_sha256$'):
            anggota.password_hash = make_password(self.cleaned_data['password_hash'])
        if commit:
            anggota.save()
        return anggota
