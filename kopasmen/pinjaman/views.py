from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Pinjaman, Angsuran, Anggota, Admin
from .forms import PinjamanForm
from django.db.models import Sum

def pinjaman_list(request):
    pinjaman_list = Pinjaman.objects.all()

    pinjaman_dict = {}
    for pinjaman in pinjaman_list:
        anggota = pinjaman.nomor_anggota.nama
        nomor_anggota = pinjaman.nomor_anggota.nomor_anggota
        jenis_pinjaman = pinjaman.id_jenis_pinjaman.nama_jenis
        if anggota not in pinjaman_dict:
            pinjaman_dict[anggota] = {
                'nomor_anggota': nomor_anggota,
                'Reguler': 0,
                'Khusus': 0,
                'Barang': 0,
                'pinjaman_ids': []
            }
        
        jumlah_cicilan_terbayar = Angsuran.objects.filter(id_pinjaman=pinjaman).count()
        angsuran_pokok = pinjaman.angsuran_per_bulan or 0
        sisa_pinjaman = pinjaman.jumlah_pinjaman - (jumlah_cicilan_terbayar * angsuran_pokok)

        if jenis_pinjaman == 'Reguler':
            pinjaman_dict[anggota]['Reguler'] += sisa_pinjaman
        elif jenis_pinjaman == 'Khusus':
            pinjaman_dict[anggota]['Khusus'] += sisa_pinjaman
        elif jenis_pinjaman == 'Barang':
            pinjaman_dict[anggota]['Barang'] += sisa_pinjaman

    return render(request, 'pinjaman_list.html', {'pinjaman_dict': pinjaman_dict})

def pinjaman_anggota(request, nomor_anggota=None):
    anggota_data = {}
    all_pinjaman_list = []

    if nomor_anggota:
        anggota_list = Anggota.objects.filter(nomor_anggota=nomor_anggota)
    else:
        anggota_list = Anggota.objects.all()

    for anggota in anggota_list:
        pinjaman_data = {
            'nomor_anggota': anggota.nomor_anggota,
            'nama': anggota.nama,
            'tanggal_meminjam': None,
            'pinjaman_reguler_awal': 0,
            'angsuran_reguler': 0,
            'jasa_persen_reguler': 0,
            'jasa_reguler': 0,
            'total_reguler': 0,
            'sisa_reguler': 0,
            'status_reguler': '-',
            'pinjaman_reguler_id': None,
            'pinjaman_khusus_awal': 0,
            'angsuran_khusus': 0,
            'jasa_persen_khusus': 0,
            'jasa_khusus': 0,
            'total_khusus': 0,
            'sisa_khusus': 0,
            'status_khusus': '-',
            'pinjaman_khusus_id': None,
            'pinjaman_barang_awal': 0,
            'angsuran_barang': 0,
            'jasa_persen_barang': 0,
            'jasa_barang': 0,
            'total_barang': 0,
            'sisa_barang': 0,
            'status_barang': '-',
            'pinjaman_barang_id': None,
        }

        for pinjaman in Pinjaman.objects.filter(nomor_anggota=anggota).order_by('tanggal_meminjam'):
            if pinjaman_data['tanggal_meminjam'] is None:
                pinjaman_data['tanggal_meminjam'] = pinjaman.tanggal_meminjam

            angsuran_pokok = pinjaman.angsuran_per_bulan or 0
            jumlah_cicilan_terbayar = Angsuran.objects.filter(id_pinjaman=pinjaman).count()
            total_pokok_bayar = jumlah_cicilan_terbayar * angsuran_pokok
            sisa_pinjaman = pinjaman.jumlah_pinjaman - total_pokok_bayar

            if sisa_pinjaman <= 0 and pinjaman.status != "Lunas":
                pinjaman.status = "Lunas"
                pinjaman.save()

            if pinjaman.id_kategori_jasa.kategori_jasa.lower() == "turunan":
                jasa_rupiah = sisa_pinjaman * (pinjaman.jasa_persen / 100 if pinjaman.jasa_persen else 0)
            else:
                jasa_rupiah = pinjaman.jumlah_pinjaman * (pinjaman.jasa_persen / 100 if pinjaman.jasa_persen else 0)

            jenis = pinjaman.id_jenis_pinjaman.nama_jenis
            all_pinjaman_list.append({'id': pinjaman.id_pinjaman, 'jenis': jenis})

            if jenis == 'Reguler':
                pinjaman_data.update({
                    'pinjaman_reguler_awal': pinjaman.jumlah_pinjaman,
                    'angsuran_reguler': angsuran_pokok,
                    'jasa_persen_reguler': pinjaman.jasa_persen,
                    'jasa_reguler': round(jasa_rupiah, 2),
                    'total_reguler': round(angsuran_pokok + jasa_rupiah, 2),
                    'sisa_reguler': sisa_pinjaman,
                    'status_reguler': pinjaman.status,
                    'pinjaman_reguler_id': pinjaman.id_pinjaman
                })
            elif jenis == 'Khusus':
                pinjaman_data.update({
                    'pinjaman_khusus_awal': pinjaman.jumlah_pinjaman,
                    'angsuran_khusus': angsuran_pokok,
                    'jasa_persen_khusus': pinjaman.jasa_persen,
                    'jasa_khusus': round(jasa_rupiah, 2),
                    'total_khusus': round(angsuran_pokok + jasa_rupiah, 2),
                    'sisa_khusus': sisa_pinjaman,
                    'status_khusus': pinjaman.status,
                    'pinjaman_khusus_id': pinjaman.id_pinjaman
                })
            elif jenis == 'Barang':
                pinjaman_data.update({
                    'pinjaman_barang_awal': pinjaman.jumlah_pinjaman,
                    'angsuran_barang': angsuran_pokok,
                    'jasa_persen_barang': pinjaman.jasa_persen,
                    'jasa_barang': round(jasa_rupiah, 2),
                    'total_barang': round(angsuran_pokok + jasa_rupiah, 2),
                    'sisa_barang': sisa_pinjaman,
                    'status_barang': pinjaman.status,
                    'pinjaman_barang_id': pinjaman.id_pinjaman
                })

        anggota_data[anggota.nomor_anggota] = pinjaman_data

    context = {
        'anggota_data': anggota_data,
        'all_pinjaman_list': all_pinjaman_list,
    }
    return render(request, 'pinjaman_anggota.html', context)

def detail_pinjaman(request, id_pinjaman):
    pinjaman = get_object_or_404(Pinjaman, id_pinjaman=id_pinjaman)
    angsuran_pokok = pinjaman.angsuran_per_bulan or 0

    jumlah_cicilan_terbayar = Angsuran.objects.filter(id_pinjaman=pinjaman).count()
    total_pokok_bayar = jumlah_cicilan_terbayar * angsuran_pokok
    sisa_pinjaman = pinjaman.jumlah_pinjaman - total_pokok_bayar

    if pinjaman.id_kategori_jasa.kategori_jasa.lower() == "turunan":
        jasa_rupiah = sisa_pinjaman * (pinjaman.jasa_persen / 100 if pinjaman.jasa_persen else 0)
    else:
        jasa_rupiah = pinjaman.jumlah_pinjaman * (pinjaman.jasa_persen / 100 if pinjaman.jasa_persen else 0)

    cicilan_total = angsuran_pokok + jasa_rupiah

    total_bayar = Angsuran.objects.filter(id_pinjaman=pinjaman).aggregate(
        total=Sum('jumlah_bayar')
    )['total'] or 0

    return render(request, 'detail_pinjaman.html', {
        'pinjaman': pinjaman,
        'nama_anggota': pinjaman.nomor_anggota.nama,
        'jenis_pinjaman': pinjaman.id_jenis_pinjaman.nama_jenis,
        'jasa': round(jasa_rupiah, 2),
        'cicilan_total': round(cicilan_total, 2),
        'total_bayar': total_bayar,
        'sisa_pinjaman': sisa_pinjaman,
        'kategori_pinjaman': pinjaman.id_kategori_jasa.kategori_jasa
    })

def tambah_pinjaman(request):
    if request.method == "POST":
        form = PinjamanForm(request.POST)
        if form.is_valid():
            pinjaman = form.save(commit=False) 
            jumlah_pinjaman = pinjaman.jumlah_pinjaman
            jasa_persen = form.cleaned_data.get('jasa_persen')
            if pinjaman.id_kategori_jasa.kategori_jasa.lower() == "turunan":
                jasa_rupiah = jumlah_pinjaman * (jasa_persen / 100 if jasa_persen else 0) 
            else:
                jasa_rupiah = jumlah_pinjaman * (jasa_persen / 100 if jasa_persen else 0)

            pinjaman.jasa_rupiah = round(jasa_rupiah, 2)
            pinjaman.save()
            return redirect('pinjaman_list')
    else:
        form = PinjamanForm()

    return render(request, 'pinjaman_form.html', {'form': form})

def bayar_pinjaman(request, id_pinjaman):
    pinjaman = get_object_or_404(Pinjaman, id_pinjaman=id_pinjaman)

    admin_id = request.session.get("admin_id")
    if not admin_id:
        messages.error(request, "Anda harus login sebagai admin terlebih dahulu.")
        return redirect("login")
    admin_login = get_object_or_404(Admin, id_admin=admin_id)

    angsuran_pokok = pinjaman.angsuran_per_bulan or 0
    jumlah_cicilan_terbayar = Angsuran.objects.filter(id_pinjaman=pinjaman).count()
    sisa_pinjaman = pinjaman.jumlah_pinjaman - (jumlah_cicilan_terbayar * angsuran_pokok)

    if pinjaman.id_kategori_jasa.kategori_jasa.lower() == "turunan":
        jasa_rupiah = sisa_pinjaman * (pinjaman.jasa_persen / 100 if pinjaman.jasa_persen else 0)
    else:
        jasa_rupiah = pinjaman.jumlah_pinjaman * (pinjaman.jasa_persen / 100 if pinjaman.jasa_persen else 0)

    jumlah_cicilan_total = angsuran_pokok + jasa_rupiah

    if request.method == "POST":
        tanggal_bayar = request.POST.get("tanggal_bayar")
        jumlah_dibayar = request.POST.get("jumlah_dibayar")
        if jumlah_dibayar and tanggal_bayar:
            Angsuran.objects.create(
                id_pinjaman=pinjaman,
                id_admin=admin_login,
                tanggal_bayar=tanggal_bayar,
                jumlah_bayar=jumlah_dibayar
            )

            total_cicilan_terbayar = Angsuran.objects.filter(id_pinjaman=pinjaman).count()
            sisa_akhir = pinjaman.jumlah_pinjaman - (total_cicilan_terbayar * angsuran_pokok)
            if sisa_akhir <= 0:
                pinjaman.status = "Lunas"
                pinjaman.save()

            messages.success(request, "Pembayaran angsuran berhasil dicatat.")
            return redirect("pinjaman_list")

    return render(request, "bayar_pinjaman.html", {
        "pinjaman": pinjaman,
        "total_bayar": Angsuran.objects.filter(id_pinjaman=pinjaman).aggregate(
            total=Sum('jumlah_bayar')
        )['total'] or 0,
        "sisa_pinjaman": sisa_pinjaman,
        "angsuran_pokok": angsuran_pokok,
        "jasa_rupiah": round(jasa_rupiah, 2),
        "jumlah_cicilan_total": round(jumlah_cicilan_total, 2),
        "admin_login": admin_login,
    })


def detail_pembayaran(request, pembayaran_id):
    pembayaran = get_object_or_404(Angsuran, id_pembayaran=pembayaran_id)
    pinjaman = pembayaran.id_pinjaman
    angsuran_pokok = pinjaman.angsuran_per_bulan or 0

    semua_cicilan = Angsuran.objects.filter(id_pinjaman=pinjaman).order_by('tanggal_bayar', 'id_pembayaran')

    sisa_pinjaman = pinjaman.jumlah_pinjaman
    sisa_sebelum = sisa_pinjaman
    sisa_setelah = sisa_pinjaman

    for cicilan in semua_cicilan:
        if cicilan.id_pembayaran == pembayaran.id_pembayaran:
            sisa_sebelum = sisa_pinjaman
            sisa_pinjaman -= angsuran_pokok
            sisa_setelah = sisa_pinjaman
            break
        else:
            sisa_pinjaman -= angsuran_pokok

    if pinjaman.id_kategori_jasa.kategori_jasa.lower() == "turunan":
        jasa_rupiah = sisa_sebelum * (pinjaman.jasa_persen / 100 if pinjaman.jasa_persen else 0)
    else:
        jasa_rupiah = pinjaman.jumlah_pinjaman * (pinjaman.jasa_persen / 100 if pinjaman.jasa_persen else 0)

    return render(request, 'detail_pembayaran.html', {
        'pembayaran': pembayaran,
        'sisa_sebelum': sisa_sebelum,
        'sisa_setelah': sisa_setelah,
        'jasa_rupiah': round(jasa_rupiah, 2),
    })