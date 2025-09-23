from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.utils.timezone import now
import calendar
from datetime import datetime, time

from simpanan.models import Simpanan
from pinjaman.models import Pinjaman, Angsuran
from anggota.models import Anggota
from admin_koperasi.models import Admin


def laporan_gabungan(request):
    if not request.session.get('admin_id'):
        return redirect('admin_koperasi:login')

    username = request.session.get('admin_username')
    role = request.session.get('admin_role')

    bulan = int(request.GET.get("bulan", now().month))
    tahun_bulan = int(request.GET.get("tahun", now().year))
    tahun_tahunan = int(request.GET.get("tahun_tahunan", now().year))

    tahun_range = list(range(2020, now().year + 1))
    bulan_list = list(range(1, 13))

    # batas akhir bulan dipilih
    last_day_bulan = calendar.monthrange(tahun_bulan, bulan)[1]
    tanggal_akhir_bulan = datetime.combine(
        datetime(tahun_bulan, bulan, last_day_bulan),
        time(23, 59, 59)
    )

    # batas akhir tahun dipilih
    tanggal_akhir_tahun = datetime.combine(
        datetime(tahun_tahunan, 12, 31),
        time(23, 59, 59)
    )

    def generate_laporan(anggota_list, akhir=None):
        laporan = []
        for idx, anggota in enumerate(anggota_list, start=1):
            # ===================== SIMPANAN =====================
            filter_args = {"anggota": anggota}
            if akhir:
                filter_args["tanggal_menyimpan__lte"] = akhir

            pokok = Simpanan.objects.filter(
                **filter_args, jenis_simpanan__nama_jenis="Pokok"
            ).aggregate(total=Sum("jumlah_menyimpan"))["total"] or 0
            wajib = Simpanan.objects.filter(
                **filter_args, jenis_simpanan__nama_jenis="Wajib"
            ).aggregate(total=Sum("jumlah_menyimpan"))["total"] or 0
            sukarela = Simpanan.objects.filter(
                **filter_args, jenis_simpanan__nama_jenis="Sukarela"
            ).aggregate(total=Sum("jumlah_menyimpan"))["total"] or 0
            total_simpanan = pokok + wajib + sukarela

            # ===================== PINJAMAN =====================
            filter_pinj = {"nomor_anggota": anggota}
            if akhir:
                filter_pinj["tanggal_meminjam__lte"] = akhir

            total_reguler = total_khusus = total_barang = 0

            for jenis in ["Reguler", "Khusus", "Barang"]:
                pinjaman_qs = Pinjaman.objects.filter(
                    **filter_pinj, id_jenis_pinjaman__nama_jenis=jenis
                )

                for pin in pinjaman_qs:
                    # Hitung sisa pokok
                    angsuran_pokok = pin.angsuran_per_bulan or 0
                    jumlah_cicilan_terbayar = Angsuran.objects.filter(
                        id_pinjaman=pin, tanggal_bayar__lte=akhir
                    ).count()
                    sisa_pinjaman = pin.jumlah_pinjaman - (jumlah_cicilan_terbayar * angsuran_pokok)

                    if sisa_pinjaman < 0:
                        sisa_pinjaman = 0

                    # Hitung jasa terbaru
                    if pin.id_kategori_jasa.kategori_jasa.lower() == "turunan":
                        jasa_rupiah = sisa_pinjaman * (pin.jasa_persen / 100 if pin.jasa_persen else 0)
                    else:
                        jasa_rupiah = pin.jumlah_pinjaman * (pin.jasa_persen / 100 if pin.jasa_persen else 0)

                    # Total kewajiban saat ini = sisa pokok + jasa terbaru
                    sisa = sisa_pinjaman + jasa_rupiah

                    if jenis == "Reguler":
                        total_reguler += sisa
                    elif jenis == "Khusus":
                        total_khusus += sisa
                    elif jenis == "Barang":
                        total_barang += sisa


            total_pinjaman = total_reguler + total_khusus + total_barang

            laporan.append({
                "no": idx,
                "nama": anggota.nama,
                "simpanan": {
                    "pokok": pokok,
                    "wajib": wajib,
                    "sukarela": sukarela,
                    "total": total_simpanan
                },
                "pinjaman": {
                    "reguler": total_reguler,
                    "khusus": total_khusus,
                    "barang": total_barang,
                    "total": total_pinjaman
                },
            })
        return laporan

    anggota_list = Anggota.objects.all().order_by("nama")
    laporan_bulanan = generate_laporan(anggota_list, akhir=tanggal_akhir_bulan)
    laporan_tahunan = generate_laporan(anggota_list, akhir=tanggal_akhir_tahun)

    context = {
        "username": username,
        "role": role,
        "bulan": bulan,
        "bulan_list": bulan_list,
        "tahun_bulan": tahun_bulan,
        "tahun_range": tahun_range,
        "tahun_tahunan": tahun_tahunan,
        "tanggal_akhir_bulan": tanggal_akhir_bulan.strftime("%d/%m/%Y"),
        "tanggal_akhir_tahun": tanggal_akhir_tahun.strftime("%d/%m/%Y"),
        "laporan_bulanan": laporan_bulanan,
        "laporan_tahunan": laporan_tahunan,
    }

    return render(request, "laporan.html", context)
