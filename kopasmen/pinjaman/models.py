from django.db import models
from anggota.models import Anggota 
from admin_koperasi.models import Admin 

class JenisPinjaman(models.Model):
    JENIS_PINJAMAN_CHOICES = [
        ('Reguler', 'Reguler'),
        ('Khusus', 'Khusus'),
        ('Barang', 'Barang'),
    ]
    KATEGORI_JASA_CHOICES = [
        ('flat', 'Flat'),
        ('turunan', 'Turunan'),
    ]
    
    id_jenis_pinjaman = models.BigAutoField(primary_key=True)
    nama_jenis = models.CharField(max_length=50, choices=JENIS_PINJAMAN_CHOICES)
    jasa = models.DecimalField(max_digits=5, decimal_places=2)
    kategori_jasa = models.CharField(max_length=20, choices=KATEGORI_JASA_CHOICES, default='flat') 

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
    angsuran_per_bulan = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    lama_peminjaman = models.IntegerField(default=1)
    kategori_jasa = models.CharField(max_length=20, choices=[('flat', 'Flat'), ('turunan', 'Turunan')], default='flat')
    jasa_persen = models.DecimalField(max_digits=5, decimal_places=2)
    jasa_pinjam = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    tanggal_meminjam = models.DateField()
    jatuh_tempo = models.DateField()
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'Pinjaman'

    def __str__(self):
        return f"Pinjaman {self.id_pinjaman} - {self.nomor_anggota}"

    def hitung_jasa(self):
        return self.jasa_pinjam

    def hitung_angsuran_per_bulan(self):
        if self.lama_peminjaman > 0:
            return (self.jumlah_pinjaman + self.hitung_jasa()) / self.lama_peminjaman
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
