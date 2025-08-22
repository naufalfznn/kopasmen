from django.shortcuts import render, redirect
from .models import Pinjaman, JenisPinjaman
from .forms import PinjamanForm

def pinjaman_list(request):
    pinjaman = Pinjaman.objects.all()
    return render(request, 'pinjaman_list.html', {'pinjaman_list': pinjaman})

from django.contrib.auth.decorators import user_passes_test

def user_is_admin(user):
    return hasattr(user, 'admin')

def tambah_pinjaman(request):
    jenis_pinjaman = JenisPinjaman.objects.all()

    if request.method == 'POST':
        form = PinjamanForm(request.POST)
        if form.is_valid():
            form.instance.id_admin = request.user
            form.save()
            return redirect('pinjaman_list')
    else:
        form = PinjamanForm()

    return render(request, 'pinjaman_form.html', {
        'form': form,
        'jenis_pinjaman': jenis_pinjaman
    })