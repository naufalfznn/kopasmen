from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Pinjaman, Angsuran, Anggota
from .forms import PinjamanForm

def pinjaman_list(request):
    pinjaman_list = Pinjaman.objects.all()

    pinjaman_dict = {}
    for pinjaman in pinjaman_list:
        anggota = pinjaman.nomor_anggota.nama
        nomor_anggota = pinjaman.nomor_anggota.nomor_anggota
        jenis_pinjaman = pinjaman.id_jenis_pinjaman.nama_jenis
        if anggota not in pinjaman_dict:
            pinjaman_dict[anggota] = {'nomor_anggota': nomor_anggota, 'Reguler': 0, 'Khusus': 0, 'Barang': 0, 'pinjaman_ids': []}
        
        if jenis_pinjaman == 'Reguler':
            pinjaman_dict[anggota]['Reguler'] += pinjaman.jumlah_pinjaman
        elif jenis_pinjaman == 'Khusus':
            pinjaman_dict[anggota]['Khusus'] += pinjaman.jumlah_pinjaman
        elif jenis_pinjaman == 'Barang':
            pinjaman_dict[anggota]['Barang'] += pinjaman.jumlah_pinjaman

        pinjaman_dict[anggota]['pinjaman_ids'].append(pinjaman.id_pinjaman)

    return render(request, 'pinjaman_list.html', {'pinjaman_dict': pinjaman_dict})

def pinjaman_anggota(request):
    anggota_data = {}

    for anggota in Anggota.objects.all():
        pinjaman_data = {
            'nomor_anggota': anggota.nomor_anggota,
            'nama': anggota.nama,
            'pinjaman_reguler': 0,
            'pinjaman_khusus': 0,
            'pinjaman_barang': 0,
            'angsuran_reguler': 0,
            'angsuran_khusus': 0,
            'angsuran_barang': 0,
            'jasa_reguler': 0,
            'jasa_khusus': 0,
            'jasa_barang': 0,
            'total_cicilan_jasa': 0,
            'status': 'Belum Lunas',
            'pinjaman_ids': [],
            'tanggal_meminjam': None,
            'jasa_persen': 0,  # Ensure jasa_persen is initialized
        }

        for pinjaman in Pinjaman.objects.filter(nomor_anggota=anggota):
            if pinjaman.status == 'Lunas':
                pinjaman_data['status'] = 'Lunas'
            if pinjaman_data['tanggal_meminjam'] is None:
                pinjaman_data['tanggal_meminjam'] = pinjaman.tanggal_meminjam

            if pinjaman.id_jenis_pinjaman.nama_jenis == 'Reguler':
                pinjaman_data['pinjaman_reguler'] += pinjaman.jumlah_pinjaman
                pinjaman_data['angsuran_reguler'] = pinjaman.angsuran_per_bulan or 0
                pinjaman_data['jasa_reguler'] = pinjaman.jasa_rupiah or 0
                pinjaman_data['jasa_persen'] = pinjaman.jasa_persen or 0  # Capture jasa persen if available
            elif pinjaman.id_jenis_pinjaman.nama_jenis == 'Khusus':
                pinjaman_data['pinjaman_khusus'] += pinjaman.jumlah_pinjaman
                pinjaman_data['angsuran_khusus'] = pinjaman.angsuran_per_bulan or 0
                pinjaman_data['jasa_khusus'] = pinjaman.jasa_rupiah or 0
                pinjaman_data['jasa_persen'] = pinjaman.jasa_persen or 0
            elif pinjaman.id_jenis_pinjaman.nama_jenis == 'Barang':
                pinjaman_data['pinjaman_barang'] += pinjaman.jumlah_pinjaman
                pinjaman_data['angsuran_barang'] = pinjaman.angsuran_per_bulan or 0
                pinjaman_data['jasa_barang'] = pinjaman.jasa_rupiah or 0
                pinjaman_data['jasa_persen'] = pinjaman.jasa_persen or 0

            pinjaman_data['pinjaman_ids'].append(pinjaman.id_pinjaman)

        pinjaman_data['total_cicilan_jasa'] = (
            (pinjaman_data['angsuran_reguler'] or 0) + (pinjaman_data['jasa_reguler'] or 0) +
            (pinjaman_data['angsuran_khusus'] or 0) + (pinjaman_data['jasa_khusus'] or 0) +
            (pinjaman_data['angsuran_barang'] or 0) + (pinjaman_data['jasa_barang'] or 0)
        )

        anggota_data[anggota.nomor_anggota] = pinjaman_data

    return render(request, 'pinjaman_anggota.html', {'anggota_data': anggota_data})


def tambah_pinjaman(request):
    if request.method == "POST":
        form = PinjamanForm(request.POST)
        if form.is_valid():
            pinjaman = form.save(commit=False)  # Jangan simpan dulu, biar bisa dihitung jasa

            # Mengambil nilai yang sudah diinput
            jumlah_pinjaman = pinjaman.jumlah_pinjaman
            jasa_persen = form.cleaned_data.get('jasa_persen')  # Ambil persentase jasa

            # Pastikan nilai jasa_persen valid dan hitung jasa_rupiah jika persentase ada
            if jasa_persen is not None and jumlah_pinjaman is not None:
                jasa_rupiah = jumlah_pinjaman * (jasa_persen / 100)
                pinjaman.jasa_rupiah = round(jasa_rupiah, 2)  # Simpan jasa_rupiah yang dihitung

            pinjaman.save()  # Simpan pinjaman dengan jasa_rupiah yang sudah dihitung
            return redirect('pinjaman_list')  # Redirect ke halaman list pinjaman
    else:
        form = PinjamanForm()  # Form kosong jika request bukan POST

    return render(request, 'pinjaman_form.html', {'form': form})  # Kembalikan form ke template



def detail_pinjaman(request, id_pinjaman):
    pinjaman = get_object_or_404(Pinjaman, id_pinjaman=id_pinjaman)
    return render(request, 'detail_pinjaman.html', {'pinjaman': pinjaman})

def bayar_pinjaman(request, id_pinjaman):
    pinjaman = get_object_or_404(Pinjaman, id_pinjaman=id_pinjaman)

    if request.method == 'POST':
        form = PinjamanForm(request.POST)
        if form.is_valid():
            jumlah_dibayar = form.cleaned_data['jumlah_dibayar']
            tanggal_bayar = form.cleaned_data['tanggal_bayar']

            angsuran = Angsuran(
                id_pinjaman=pinjaman,
                id_admin=request.user.admin,
                jumlah_bayar=jumlah_dibayar,
                tanggal_bayar=tanggal_bayar
            )
            angsuran.save()

            pinjaman.jumlah_pinjaman -= jumlah_dibayar
            pinjaman.save()

            if pinjaman.jumlah_pinjaman <= 0:
                pinjaman.status = 'Lunas'
                pinjaman.save()

            messages.success(request, f"Pembayaran sebesar {jumlah_dibayar} berhasil!")
            return redirect('pinjaman:pinjaman_list')
    else:
        form = PinjamanForm()

    return render(request, 'bayar_pinjaman.html', {'pinjaman': pinjaman, 'form': form})