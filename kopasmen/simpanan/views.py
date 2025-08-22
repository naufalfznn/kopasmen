from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q, F
from .forms import SimpananForm
from .models import Simpanan, Anggota

def tambah_simpanan(request):
    if request.method == "POST":
        form = SimpananForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("daftar_simpanan")
    else:
        form = SimpananForm()
    return render(request, "simpanan_form.html", {"form": form})


def daftar_simpanan(request):
    data = (
        Simpanan.objects.values(
            kode_anggota=F('anggota__nomor_anggota'),
            no_anggota=F('anggota__nomor_anggota'),
            nama_anggota=F('anggota__nama')
        )
        .annotate(
            total_pokok=Sum('jumlah_menyimpan', filter=Q(jenis_simpanan__id_jenis_simpanan=1)),
            total_wajib=Sum('jumlah_menyimpan', filter=Q(jenis_simpanan__id_jenis_simpanan=2)),
            total_sukarela=Sum('jumlah_menyimpan', filter=Q(jenis_simpanan__id_jenis_simpanan=3)),
        )
    )
    return render(request, "daftar_simpanan.html", {"data": data})


def detail_simpanan(request, nomor_anggota):
    anggota = get_object_or_404(Anggota, nomor_anggota=nomor_anggota)
    simpanan = Simpanan.objects.filter(anggota=anggota)


    total_pokok = simpanan.filter(jenis_simpanan__nama_jenis="Simpanan Pokok").aggregate(
        total=Sum('jumlah_menyimpan')
    )['total'] or 0

    total_wajib = simpanan.filter(jenis_simpanan__nama_jenis="Simpanan Wajib").aggregate(
        total=Sum('jumlah_menyimpan')
    )['total'] or 0

    total_sukarela = simpanan.filter(jenis_simpanan__nama_jenis="Simpanan Sukarela").aggregate(
        total=Sum('jumlah_menyimpan')
    )['total'] or 0

    context = {
        "anggota": anggota,
        "simpanan": simpanan.order_by('-tanggal_menyimpan'),
        "total_pokok": total_pokok,
        "total_wajib": total_wajib,
        "total_sukarela": total_sukarela,
        "tanggal_input": simpanan.first().tanggal_menyimpan if simpanan.exists() else None,
        "petugas_input": simpanan.first().admin.username if simpanan.exists() and simpanan.first().admin else "-",
    }

    return render(request, "detail_simpanan.html", context)


