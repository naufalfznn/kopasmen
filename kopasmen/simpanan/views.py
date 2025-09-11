from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q, F
from .forms import SimpananForm
from .models import Simpanan, Anggota
from .forms import EditSimpananForm
from django.db.models import Sum
from django.contrib import messages

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

def edit_simpanan(request, nomor_anggota):
    anggota = get_object_or_404(Anggota, nomor_anggota=nomor_anggota)
    simpanan_list = Simpanan.objects.filter(anggota=anggota)

    # hitung total per jenis
    pokok = simpanan_list.filter(jenis_simpanan__nama_jenis="Simpanan Pokok").aggregate(total=Sum("jumlah_menyimpan"))["total"] or 0
    wajib = simpanan_list.filter(jenis_simpanan__nama_jenis="Simpanan Wajib").aggregate(total=Sum("jumlah_menyimpan"))["total"] or 0
    sukarela = simpanan_list.filter(jenis_simpanan__nama_jenis="Simpanan Sukarela").aggregate(total=Sum("jumlah_menyimpan"))["total"] or 0

    if request.method == "POST":
        form = EditSimpananForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['simpanan_pokok']:
                Simpanan.objects.create(
                    anggota=anggota,
                    admin=cd['admin'],
                    jenis_simpanan_id=1, 
                    tanggal_menyimpan=cd['tanggal_menyimpan'],
                    jumlah_menyimpan=cd['simpanan_pokok'],
                )
            if cd['simpanan_wajib']:
                Simpanan.objects.create(
                    anggota=anggota,
                    admin=cd['admin'],
                    jenis_simpanan_id=2, 
                    tanggal_menyimpan=cd['tanggal_menyimpan'],
                    jumlah_menyimpan=cd['simpanan_wajib'],
                )
            if cd['simpanan_sukarela']:
                Simpanan.objects.create(
                    anggota=anggota,
                    admin=cd['admin'],
                    jenis_simpanan_id=3,
                    tanggal_menyimpan=cd['tanggal_menyimpan'],
                    jumlah_menyimpan=cd['simpanan_sukarela'],
                )
            return redirect("detail_simpanan", nomor_anggota=nomor_anggota)
    else:
        form = EditSimpananForm(initial={
            "anggota": anggota.pk,
            "admin": simpanan_list.first().admin if simpanan_list.exists() else None,
            "tanggal_menyimpan": simpanan_list.first().tanggal_menyimpan if simpanan_list.exists() else None,
            "simpanan_pokok": pokok,
            "simpanan_wajib": wajib,
            "simpanan_sukarela": sukarela,
        })

    return render(request, "edit_simpanan.html", {
        "form": form,
        "anggota": anggota,
    })

def hapus_simpanan(request, nomor_anggota):
    anggota = get_object_or_404(Anggota, nomor_anggota=nomor_anggota)
    simpanan = Simpanan.objects.filter(anggota=anggota)

    if request.method == "POST":
        count, _ = simpanan.delete()
        messages.success(request, f"{count} data simpanan untuk {anggota.nama} berhasil dihapus.")
        return redirect("daftar_simpanan")

    return render(request, "hapus_simpanan.html", {
        "anggota": anggota,
        "simpanan": simpanan,
    })
