from django.shortcuts import render, redirect, get_object_or_404

from admin_koperasi.models import Admin
from .models import Anggota
from .forms import AdminForm, AnggotaForm
from django.db import connection

def kelola_akun_view(request):
    anggotas = Anggota.objects.all() 
    admins = Admin.objects.all()
    return render(request, 'kelola_akun.html', {'anggotas': anggotas, 'admins': admins})

def tambah_admin(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kelola_akun') 
    else:
        form = AdminForm()
    return render(request, 'form_admin.html', {'form': form})

def edit_admin(request, id_admin):
    admin = get_object_or_404(Admin, id_admin=id_admin)
    form = AdminForm(request.POST or None, instance=admin)
    if form.is_valid():
        form.save()
        return redirect('kelola_akun')
    return render(request, 'form_admin.html', {'form': form, 'judul': 'Edit Admin'})

def hapus_admin(request, id_admin):
    admin = get_object_or_404(Admin, id_admin=id_admin)
    admin.delete()
    return redirect('kelola_akun')

def detail_admin(request, id_admin):
    admin = get_object_or_404(Admin, id_admin=id_admin)
    all_admins = Admin.objects.order_by('id_admin')
    nomor_urut = list(all_admins).index(admin) + 1  

    context = {
        'admin': admin,
        'nomor_urut': nomor_urut,
    }
    return render(request, 'detailA.html', context)

def tambah_anggota(request):
    if request.method == 'POST':
        form = AnggotaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kelola_akun')
    else:
        form = AnggotaForm() 
    return render(request, 'form_admin.html', {'form': form, 'judul': 'Tambah Anggota'})

def anggota_detail(request, nomor_anggota):
    try:
        anggota = Anggota.objects.get(nomor_anggota=nomor_anggota)
        return render(request, 'detail.html', {'anggota': anggota})
    except Anggota.DoesNotExist:
        return render(request, 'detail.html', {'error': 'Anggota not found'})
    
def edit_anggota(request, nomor_anggota):
    anggota = get_object_or_404(Anggota, nomor_anggota=nomor_anggota)
    form = AnggotaForm(request.POST or None, instance=anggota)
    if form.is_valid():
        form.save()
        return redirect('kelola_akun')
    return render(request, 'form_anggota.html', {'form': form, 'judul': 'Edit Anggota'})


def hapus_anggota(request, nomor_anggota):
    anggota = get_object_or_404(Anggota, nomor_anggota=nomor_anggota)
    anggota.delete()
    return redirect('kelola_akun')

def detail_anggota(request, nomor_anggota):
    anggota = get_object_or_404(Anggota, nomor_anggota=nomor_anggota)
    return render(request, 'detail.html', {'anggota': anggota})