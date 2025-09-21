from django.shortcuts import render, redirect
from django.db.models import Sum
from django.utils.timezone import now
import calendar
from datetime import datetime, time

from simpanan.models import Simpanan
from pinjaman.models import Pinjaman, Angsuran
from anggota.models import Anggota


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

    last_day_bulan = calendar.monthrange(tahun_bulan, bulan)[1]
    tanggal_akhir_bulan = datetime.combine(
        datetime(tahun_bulan, bulan, last_day_bulan),
        time(23, 59, 59)
    )

    tanggal_akhir_tahun = datetime.combine(
        datetime(tahun_tahunan, 12, 31),
        time(23, 59, 59)
    )

    def generate_laporan(anggota_list, akhir=None):
        laporan = []
        for idx, anggota in enumerate(anggota_list, start=1):
            # SIMPANAN
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

            # PINJAMAN
            filter_pinj = {"nomor_anggota": anggota}
            if akhir:
                filter_pinj["tanggal_meminjam__lte"] = akhir

            total_reguler = total_khusus = total_barang = 0

            for jenis in ["reguler", "khusus", "barang"]:
                pinjaman_qs = Pinjaman.objects.filter(
                    **filter_pinj, id_jenis_pinjaman__nama_jenis=jenis
                )

                for pin in pinjaman_qs:
                    bayar = Angsuran.objects.filter(
                        id_pinjaman=pin, tanggal_bayar__lte=akhir
                    ).aggregate(total=Sum("jumlah_bayar"))["total"] or 0

                    # sisa pinjaman (tanpa jasa)
                    sisa = pin.jumlah_pinjaman - bayar

                    # tambahkan jasa_rupiah terakhir kalau ada
                    jasa = pin.jasa_rupiah or 0
                    sisa_total = sisa + jasa

                    if jenis == "reguler":
                        total_reguler += sisa_total
                    elif jenis == "khusus":
                        total_khusus += sisa_total
                    elif jenis == "barang":
                        total_barang += sisa_total

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
