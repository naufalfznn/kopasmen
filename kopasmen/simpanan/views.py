from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q, F, Value, CharField
from django.contrib import messages
from .forms import SimpananForm, EditSimpananForm, PenarikanForm
from .models import Simpanan, Anggota, JenisSimpanan, Penarikan
from admin_koperasi.models import Admin
from django.core.paginator import Paginator
from django.db import models
from itertools import chain
from operator import attrgetter


def tambah_simpanan(request):
    """Tambah data simpanan baru"""
    if not request.session.get('admin_id'):
        return redirect('admin_koperasi:login')

    role = request.session.get('admin_role')
    username = request.session.get('admin_username')

    admins = Admin.objects.all()
    anggotas = Anggota.objects.all()

    if request.method == "POST":
        form = SimpananForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Data simpanan berhasil ditambahkan.")
            return redirect("daftar_simpanan")
    else:
        form = SimpananForm()

    context = {
        "username": username,
        "role": role,
        "admins": admins,
        "anggotas": anggotas,
        "form": form,
    }
    return render(request, "simpanan_form.html", context)


def daftar_simpanan(request):
    """Daftar total simpanan semua anggota dengan pagination (saldo aktual)"""
    if not request.session.get('admin_id'):
        return redirect('admin_koperasi:login')

    role = request.session.get('admin_role')
    username = request.session.get('admin_username')

    admins = Admin.objects.all()
    anggotas = Anggota.objects.all()

    data_list = []
    for anggota in anggotas:
        # Hitung total simpanan per jenis
        total_pokok = (
            Simpanan.objects.filter(anggota=anggota, jenis_simpanan__id_jenis_simpanan=1)
            .aggregate(total=Sum('jumlah_menyimpan'))['total'] or 0
        )
        total_wajib = (
            Simpanan.objects.filter(anggota=anggota, jenis_simpanan__id_jenis_simpanan=2)
            .aggregate(total=Sum('jumlah_menyimpan'))['total'] or 0
        )
        total_sukarela = (
            Simpanan.objects.filter(anggota=anggota, jenis_simpanan__id_jenis_simpanan=3)
            .aggregate(total=Sum('jumlah_menyimpan'))['total'] or 0
        )

        # Kurangi total penarikan
        total_penarikan_pokok = (
            Penarikan.objects.filter(anggota=anggota, jenis_simpanan__id_jenis_simpanan=1)
            .aggregate(total=Sum('jumlah_penarikan'))['total'] or 0
        )
        total_penarikan_wajib = (
            Penarikan.objects.filter(anggota=anggota, jenis_simpanan__id_jenis_simpanan=2)
            .aggregate(total=Sum('jumlah_penarikan'))['total'] or 0
        )
        total_penarikan_sukarela = (
            Penarikan.objects.filter(anggota=anggota, jenis_simpanan__id_jenis_simpanan=3)
            .aggregate(total=Sum('jumlah_penarikan'))['total'] or 0
        )

        data_list.append({
            'kode_anggota': anggota.nomor_anggota,
            'no_anggota': anggota.nomor_anggota,
            'nama_anggota': anggota.nama,
            'total_pokok': total_pokok - total_penarikan_pokok,
            'total_wajib': total_wajib - total_penarikan_wajib,
            'total_sukarela': total_sukarela - total_penarikan_sukarela,
        })

    # Pagination per 20 data
    paginator = Paginator(data_list, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'username': username,
        'role': role,
        'admins': admins,
        'anggotas': anggotas,
        'data': page_obj,      # data untuk tabel
        'page_obj': page_obj,  # untuk pagination di template
    }
    return render(request, "daftar_simpanan.html", context)



def detail_simpanan(request, id_simpanan):
    """Detail simpanan anggota lengkap dengan riwayat setoran & penarikan"""
    if not request.session.get('admin_id'):
        return redirect('admin_koperasi:login')

    role = request.session.get('admin_role')
    username = request.session.get('admin_username')

    simpanan = get_object_or_404(Simpanan, id_simpanan=id_simpanan)
    anggota = simpanan.anggota
    jenis = simpanan.jenis_simpanan

    # Ambil tanggal pertama simpanan untuk jenis ini
    first_simpanan = Simpanan.objects.filter(
        anggota=anggota, jenis_simpanan=jenis
    ).order_by('tanggal_menyimpan').first()
    tanggal_tabungan = first_simpanan.tanggal_menyimpan if first_simpanan else None

    # Ambil semua setoran dan beri field seragam
    setoran_list = Simpanan.objects.filter(
        anggota=anggota, jenis_simpanan=jenis
    ).annotate(
        jenis_trans=Value('Setoran', output_field=CharField()),
        tgl=F('tanggal_menyimpan'),
        jumlah=F('jumlah_menyimpan')
    )

    # Ambil semua penarikan dan beri field seragam
    penarikan_list = Penarikan.objects.filter(
        anggota=anggota, jenis_simpanan=jenis
    ).annotate(
        jenis_trans=Value('Penarikan', output_field=CharField()),
        tgl=F('tanggal_penarikan'),
        jumlah=F('jumlah_penarikan')
    )

    # Gabungkan setoran & penarikan, urut descending
    history = sorted(
        chain(setoran_list, penarikan_list),
        key=attrgetter('tgl'),
        reverse=True
    )

    # Hitung saldo
    total_setor = sum(h.jumlah for h in setoran_list)
    total_tarik = sum(h.jumlah for h in penarikan_list)
    saldo_jenis = total_setor - total_tarik

    context = {
        'username': username,
        'role': role,
        'simpanan': simpanan,
        'saldo_jenis': saldo_jenis,
        'history': history,
        'tanggal_tabungan': tanggal_tabungan,  # kirim ke template
    }
    return render(request, "detail_simpanan.html", context)



def edit_simpanan(request, nomor_anggota):
    if not request.session.get('admin_id'):
        return redirect('admin_koperasi:login')

    role = request.session.get('admin_role')
    username = request.session.get('admin_username')

    anggota = get_object_or_404(Anggota, nomor_anggota=nomor_anggota)
    simpanan = Simpanan.objects.filter(anggota=anggota).order_by('-tanggal_menyimpan')

    # Ambil jenis simpanan dari DB
    jenis_pokok = get_object_or_404(JenisSimpanan, nama_jenis="Simpanan Pokok")
    jenis_wajib = get_object_or_404(JenisSimpanan, nama_jenis="Simpanan Wajib")
    jenis_sukarela = get_object_or_404(JenisSimpanan, nama_jenis="Simpanan Sukarela")

    if request.method == "POST":
        form = EditSimpananForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            if cd['simpanan_pokok']:
                Simpanan.objects.create(
                    anggota=anggota,
                    admin=cd['admin'],
                    jenis_simpanan=jenis_pokok,
                    tanggal_menyimpan=cd['tanggal_menyimpan'],
                    jumlah_menyimpan=cd['simpanan_pokok'],
                )

            if cd['simpanan_wajib']:
                Simpanan.objects.create(
                    anggota=anggota,
                    admin=cd['admin'],
                    jenis_simpanan=jenis_wajib,
                    tanggal_menyimpan=cd['tanggal_menyimpan'],
                    jumlah_menyimpan=cd['simpanan_wajib'],
                )

            if cd['simpanan_sukarela']:
                Simpanan.objects.create(
                    anggota=anggota,
                    admin=cd['admin'],
                    jenis_simpanan=jenis_sukarela,
                    tanggal_menyimpan=cd['tanggal_menyimpan'],
                    jumlah_menyimpan=cd['simpanan_sukarela'],
                )

            # Ambil simpanan terakhir untuk redirect
            last_simpanan = Simpanan.objects.filter(anggota=anggota).order_by('-id_simpanan').first()
            messages.success(request, "Data simpanan berhasil diperbarui.")
            return redirect("detail_simpanan", id_simpanan=last_simpanan.id_simpanan)
    else:
        first_simpanan = simpanan.first()
        form = EditSimpananForm(initial={
            "anggota": anggota.pk,
            "admin": first_simpanan.admin if first_simpanan else None,
            "tanggal_menyimpan": first_simpanan.tanggal_menyimpan if first_simpanan else None,
        })

    context = {
        'username': username,
        'role': role,
        'anggota': anggota,
        'simpanan': simpanan,
        'form': form,
    }
    return render(request, "edit_simpanan.html", context)



def hapus_simpanan(request, nomor_anggota):
    """Hapus semua simpanan milik anggota"""
    if not request.session.get('admin_id'):
        return redirect('admin_koperasi:login')

    role = request.session.get('admin_role')
    username = request.session.get('admin_username')

    anggota = get_object_or_404(Anggota, nomor_anggota=nomor_anggota)
    simpanan = Simpanan.objects.filter(anggota=anggota)

    if request.method == "POST":
        count, _ = simpanan.delete()
        messages.success(request, f"{count} data simpanan untuk {anggota.nama} berhasil dihapus.")
        return redirect("daftar_simpanan")

    context = {
        'username': username,
        'role': role,
        'anggota': anggota,
        'simpanan': simpanan,
    }
    return render(request, "hapus_simpanan.html", context)

def tambah_penarikan(request, nomor_anggota, jenis):
    if not request.session.get('admin_id'):
        return redirect('admin_koperasi:login')

    role = request.session.get('admin_role')
    username = request.session.get('admin_username')

    anggota = get_object_or_404(Anggota, nomor_anggota=nomor_anggota)
    jenis_obj = get_object_or_404(JenisSimpanan, id_jenis_simpanan=jenis)

    # Hitung saldo sebelum form
    total_simpanan = (
        Simpanan.objects.filter(anggota=anggota, jenis_simpanan=jenis_obj)
        .aggregate(total=Sum("jumlah_menyimpan"))["total"] or 0
    )
    total_penarikan = (
        Penarikan.objects.filter(anggota=anggota, jenis_simpanan=jenis_obj)
        .aggregate(total=Sum("jumlah_penarikan"))["total"] or 0
    )
    saldo = total_simpanan - total_penarikan

    if request.method == "POST":
        form = PenarikanForm(request.POST)
        if form.is_valid():
            penarikan = form.save(commit=False)
            penarikan.anggota = anggota
            penarikan.jenis_simpanan = jenis_obj
            penarikan.admin = Admin.objects.filter(id_admin=request.session['admin_id']).first()

            if penarikan.jumlah_penarikan > saldo:
                messages.error(request, "Saldo tidak mencukupi untuk penarikan.")
            else:
                penarikan.save()
                messages.success(request, f"Penarikan {jenis_obj.nama_jenis} berhasil.")
                return redirect('simpanan_anggota', nomor_anggota=nomor_anggota)
        else:
            messages.error(request, "Terjadi kesalahan. Silakan periksa kembali form.")
    else:
        form = PenarikanForm(initial={
            'anggota': anggota,
            'jenis_simpanan': jenis_obj,
        })

    context = {
        'username': username,
        'role': role,
        'form': form,
        'anggota': anggota,
        'jenis': jenis_obj,
        'saldo': saldo,  # kirim saldo ke template
    }
    return render(request, 'penarikan_form.html', context)

def simpanan_anggota(request, nomor_anggota):
    if not request.session.get('admin_id'):
        return redirect('admin_koperasi:login')

    role = request.session.get('admin_role')
    username = request.session.get('admin_username')

    anggota = get_object_or_404(Anggota, nomor_anggota=nomor_anggota)

    data_saldo = []
    jenis_semua = JenisSimpanan.objects.all()  # ambil semua jenis dari master

    for jenis in jenis_semua:
        total_simpanan = (
            Simpanan.objects.filter(anggota=anggota, jenis_simpanan=jenis)
            .aggregate(total=models.Sum("jumlah_menyimpan"))["total"] or 0
        )
        total_penarikan = (
            Penarikan.objects.filter(anggota=anggota, jenis_simpanan=jenis)
            .aggregate(total=models.Sum("jumlah_penarikan"))["total"] or 0
        )

        saldo = total_simpanan - total_penarikan

        # kalau belum ada transaksi sama sekali (setoran dan penarikan = 0), skip
        if saldo == 0 and total_simpanan == 0 and total_penarikan == 0:
            continue

        last_simpanan = Simpanan.objects.filter(
            anggota=anggota, jenis_simpanan=jenis
        ).order_by('-tanggal_menyimpan').first()

        data_saldo.append({
            'jenis': jenis.nama_jenis,
            'jenis_id': jenis.id_jenis_simpanan,
            'saldo': saldo,
            'last_simpanan': last_simpanan,
        })

    context = {
        'username': username,
        'role': role,
        'anggota': anggota,
        'data_saldo': data_saldo,
    }
    return render(request, "simpanan_anggota.html", context)

