from django.shortcuts import render, redirect
from .models import Pinjaman
from .forms import PinjamanForm

def pinjaman_list(request):
    pinjaman = Pinjaman.objects.all()
    return render(request, 'pinjaman_list.html', {'pinjaman_list': pinjaman})

def tambah_pinjaman(request):
    if request.method == "POST":
        form = PinjamanForm(request.POST)
        if form.is_valid():
            pinjaman = form.save(commit=False)  
            pinjaman.save()
            return redirect('pinjaman_list')
    else:
        form = PinjamanForm()

    return render(request, 'pinjaman_form.html', {'form': form})
