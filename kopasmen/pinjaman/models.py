from django.db import models
from anggota.models import Anggota 
from admin_koperasi.models import Admin 

class JenisPinjaman(models.Model):
    JENIS_PINJAMAN_CHOICES = [
        ('Reguler', 'Reguler'),
        ('Khusus', 'Khusus'),
        ('Barang', 'Barang'),
    ]
    
    id_jenis_pinjaman = models.BigAutoField(primary_key=True)
    nama_jenis = models.CharField(max_length=50, choices=JENIS_PINJAMAN_CHOICES)
    jasa = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'Jenis_Pinjaman'

    def __str__(self):
        return self.nama_jenis

class Pinjaman(models.Model):
    id_pinjaman = models.BigAutoField(primary_key=True)
    nomor_anggota = models.ForeignKey(Anggota, on_delete=models.CASCADE)
    id_jenis_pinjaman = models.ForeignKey(JenisPinjaman, on_delete=models.CASCADE)
    id_admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    jumlah_pinjaman = models.DecimalField(max_digits=18, decimal_places=2)
    angsuran_per_bulan = models.DecimalField(max_digits=18, decimal_places=2)
    jasa = models.DecimalField(max_digits=5, decimal_places=2)
    tanggal_meminjam = models.DateField()
    jatuh_tempo = models.DateField()
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'Pinjaman'

    def __str__(self):
        return f"Pinjaman {self.id_pinjaman} - {self.nomor_anggota}"

    def hitung_jasa(self):
        if self.id_jenis_pinjaman.nama_jenis == "Reguler":
            return self.jumlah_pinjaman * 0.02 
        elif self.id_jenis_pinjaman.nama_jenis == "Khusus":
            return self.jumlah_pinjaman * 0.015 
        elif self.id_jenis_pinjaman.nama_jenis == "Barang":
            return self.jumlah_pinjaman * 0.02 
        return 0
    
    def total_bayar(self):
        total_angsur = Angsuran.objects.filter(id_pinjaman=self).aggregate(total=models.Sum('jumlah_bayar'))['total'] or 0
        return total_angsur

class Angsuran(models.Model):
    id_angsur = models.BigAutoField(primary_key=True)
    id_pinjaman = models.ForeignKey(Pinjaman, on_delete=models.CASCADE)
    id_admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    jumlah_bayar = models.DecimalField(max_digits=18, decimal_places=2)
    tanggal_bayar = models.DateField()

    class Meta:
        db_table = 'Angsuran'

    def __str__(self):
        return f"Angsuran {self.id_angsuran} - Pinjaman {self.id_pinjaman.id_pinjaman}"
