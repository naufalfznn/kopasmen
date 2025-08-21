from django.shortcuts import render
from .models import Pinjaman
from .forms import PinjamanForm

def pinjaman_list(request):
    pinjaman = Pinjaman.objects.all()
    return render(request, 'pinjaman_list.html', {'pinjaman_list': pinjaman})

from django.shortcuts import render, redirect
from .forms import PinjamanForm

def tambah_pinjaman(request):
    if request.method == 'POST':
        form = PinjamanForm(request.POST)
        if form.is_valid():
            jumlah_pinjaman = form.cleaned_data['jumlah_pinjaman']
            angsuran_per_bulan = form.cleaned_data['angsuran_per_bulan']
            jasa = form.cleaned_data['jasa']
            total_bayar = jumlah_pinjaman + (jumlah_pinjaman * (jasa / 100))

            pinjaman = form.save(commit=False)
            pinjaman.total_bayar = total_bayar
            pinjaman.save()

            return redirect('pinjaman_list')
    else:
        form = PinjamanForm()

    return render(request, 'pinjaman_form.html', {'form': form})

