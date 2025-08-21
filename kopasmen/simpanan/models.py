from django.db import models
from anggota.models import Anggota
from admin_koperasi.models import Admin


# ============================
# JENIS SIMPANAN
# ============================
class JenisSimpanan(models.Model):
    POKOK = "POKOK"
    WAJIB = "WAJIB"
    SUKARELA = "SUKARELA"

    JENIS_CHOICES = [
        (POKOK, "Simpanan Pokok"),
        (WAJIB, "Simpanan Wajib"),
        (SUKARELA, "Simpanan Sukarela"),
    ]

    id_jenis_simpanan = models.BigAutoField(primary_key=True)
    nama_jenis = models.CharField(
        max_length=50,
        choices=JENIS_CHOICES,
        unique=True
    )

    class Meta:
        db_table = "Jenis_Simpanan"

    def __str__(self):
        return self.get_nama_jenis_display()


# ============================
# SIMPANAN
# ============================
class Simpanan(models.Model):
    id_simpanan = models.BigAutoField(primary_key=True)
    anggota = models.ForeignKey(Anggota, on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True)
    jenis_simpanan = models.ForeignKey(JenisSimpanan, on_delete=models.SET_NULL, null=True, blank=True)

    tanggal_menyimpan = models.DateField()
    tanggal_menarik = models.DateField(null=True, blank=True)
    jumlah_menyimpan = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = "Simpanan"

    def __str__(self):
        return f"{self.jenis_simpanan} - {self.anggota.nama}"


# ============================
# PENARIKAN
# ============================
class Penarikan(models.Model):
    id_penarikan = models.BigAutoField(primary_key=True)
    anggota = models.ForeignKey(Anggota, on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True)
    jenis_simpanan = models.ForeignKey(JenisSimpanan, on_delete=models.SET_NULL, null=True, blank=True)

    jumlah_penarikan = models.DecimalField(max_digits=18, decimal_places=2)
    tanggal_penarikan = models.DateField()

    class Meta:
        db_table = "Penarikan"

    def __str__(self):
        return f"{self.jenis_simpanan} - {self.anggota.nama}"
