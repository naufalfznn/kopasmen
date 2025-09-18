from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q, F
from django.contrib import messages
from .forms import SimpananForm, EditSimpananForm, PenarikanForm
from .models import Simpanan, Anggota, JenisSimpanan
from admin_koperasi.models import Admin


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
    """Daftar total simpanan semua anggota"""
    if not request.session.get('admin_id'):
        return redirect('admin_koperasi:login')

    role = request.session.get('admin_role')
    username = request.session.get('admin_username')

    admins = Admin.objects.all()
    anggotas = Anggota.objects.all()

    data = (
        Simpanan.objects.values(
            kode_anggota=F('anggota__nomor_anggota'),
            no_anggota=F('anggota__nomor_anggota'),
            nama_anggota=F('anggota__nama'),
        )
        .annotate(
            total_pokok=Sum('jumlah_menyimpan', filter=Q(jenis_simpanan__id_jenis_simpanan=1)),
            total_wajib=Sum('jumlah_menyimpan', filter=Q(jenis_simpanan__id_jenis_simpanan=2)),
            total_sukarela=Sum('jumlah_menyimpan', filter=Q(jenis_simpanan__id_jenis_simpanan=3)),
        )
    )

    context = {
        'username': username,
        'role': role,
        'admins': admins,
        'anggotas': anggotas,
        'data': data,
    }
    return render(request, "daftar_simpanan.html", context)


def detail_simpanan(request, nomor_anggota=None):
    """Detail simpanan anggota (atau daftar semua kalau nomor_anggota tidak diberikan)"""
    if not request.session.get('admin_id'):
        return redirect('admin_koperasi:login')

    role = request.session.get('admin_role')
    username = request.session.get('admin_username')

    if not nomor_anggota:
        admins = Admin.objects.all()
        anggotas = Anggota.objects.all()

        data = []
        for anggota in anggotas:
            simpanan = Simpanan.objects.filter(anggota=anggota)
            data.append({
                'no_anggota': anggota.nomor_anggota,
                'nama_anggota': anggota.nama,
                'total_pokok': simpanan.filter(jenis_simpanan__nama_jenis="Simpanan Pokok").aggregate(total=Sum('jumlah_menyimpan'))['total'] or 0,
                'total_wajib': simpanan.filter(jenis_simpanan__nama_jenis="Simpanan Wajib").aggregate(total=Sum('jumlah_menyimpan'))['total'] or 0,
                'total_sukarela': simpanan.filter(jenis_simpanan__nama_jenis="Simpanan Sukarela").aggregate(total=Sum('jumlah_menyimpan'))['total'] or 0,
            })

        context = {
            'username': username,
            'role': role,
            'admins': admins,
            'anggotas': anggotas,
            'data': data,
        }
        return render(request, 'daftar_simpanan.html', context)

    anggota = get_object_or_404(Anggota, nomor_anggota=nomor_anggota)
    simpanan = Simpanan.objects.filter(anggota=anggota).order_by('-tanggal_menyimpan')

    total_pokok = simpanan.filter(jenis_simpanan__nama_jenis="Simpanan Pokok").aggregate(total=Sum('jumlah_menyimpan'))['total'] or 0
    total_wajib = simpanan.filter(jenis_simpanan__nama_jenis="Simpanan Wajib").aggregate(total=Sum('jumlah_menyimpan'))['total'] or 0
    total_sukarela = simpanan.filter(jenis_simpanan__nama_jenis="Simpanan Sukarela").aggregate(total=Sum('jumlah_menyimpan'))['total'] or 0

    if simpanan.exists():
        terakhir = simpanan.first()
        tanggal_input = terakhir.tanggal_menyimpan
        petugas_input = terakhir.admin.username if terakhir.admin else "-"
    else:
        tanggal_input = None
        petugas_input = "-"

    context = {
        'username': username,
        'role': role,
        'anggota': anggota,
        'simpanan': simpanan,
        'total_pokok': total_pokok,
        'total_wajib': total_wajib,
        'total_sukarela': total_sukarela,
        'tanggal_input': tanggal_input,
        'petugas_input': petugas_input,
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

            messages.success(request, "Data simpanan berhasil diperbarui.")
            return redirect("detail_simpanan", nomor_anggota=nomor_anggota)
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

def penarikan_simpanan(request):
    if not request.session.get('admin_id'):
        return redirect('admin_koperasi:login')

    role = request.session.get('admin_role')
    username = request.session.get('admin_username')

    if request.method == "POST":
        form = PenarikanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Penarikan simpanan berhasil disimpan!")
            return redirect('daftar_simpanan')  
    else:
        form = PenarikanForm()

    context = {
        'form': form,
        'role': role,
        'username': username,
    }
    return render(request, 'penarikan_form.html', context)

