from rest_framework import serializers
from anggota.models import Anggota
from simpanan.models import JenisSimpanan, Simpanan, Penarikan
from pinjaman.models import Pinjaman, Angsuran, JenisPinjaman, KategoriJasa
from pinjaman.models import Pinjaman, Angsuran, JenisPinjaman, KategoriJasa


class LoginSerializer(serializers.Serializer):
    nip = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ResetPasswordSerializer(serializers.Serializer):
    nip = serializers.CharField()
    password = serializers.CharField(write_only=True)


class AnggotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anggota
        fields = ["nomor_anggota", "nama", "nip", "email", "status"]


class JenisSimpananSerializer(serializers.ModelSerializer):
    class Meta:
        model = JenisSimpanan
        fields = ["id_jenis_simpanan", "nama_jenis"]


class SimpananSerializer(serializers.ModelSerializer):
    anggota = serializers.StringRelatedField()
    admin = serializers.StringRelatedField()
    jenis_simpanan = JenisSimpananSerializer()
    nominal = serializers.DecimalField(
        source="jumlah_menyimpan", max_digits=18, decimal_places=2
    )  

    class Meta:
        model = Simpanan
        fields = [
            "id_simpanan",
            "anggota",
            "admin",
            "jenis_simpanan",
            "tanggal_menyimpan",
            "tanggal_menarik",
            "nominal",
        ]


class PenarikanSerializer(serializers.ModelSerializer):
    anggota = serializers.StringRelatedField()
    admin = serializers.StringRelatedField()
    jenis_simpanan = JenisSimpananSerializer()
    nominal = serializers.DecimalField(
        source="jumlah_penarikan", max_digits=18, decimal_places=2
    )

    class Meta:
        model = Penarikan
        fields = [
            "id_penarikan",
            "anggota",
            "admin",
            "jenis_simpanan",
            "tanggal_penarikan",
            "nominal",
        ]

class JenisPinjamanSerializer(serializers.ModelSerializer):
    class Meta:
        model = JenisPinjaman
        fields = ["id_jenis_pinjaman", "nama_jenis"]

class KategoriJasaSerializer(serializers.ModelSerializer):
    class Meta:
        model = KategoriJasa
        fields = ["id_kategori_jasa", "kategori_jasa"]

class PinjamanSerializer(serializers.ModelSerializer):
    nomor_anggota = serializers.StringRelatedField()
    id_admin = serializers.StringRelatedField()
    jenis_pinjaman = JenisPinjamanSerializer(source="id_jenis_pinjaman")
    kategori_jasa = KategoriJasaSerializer(source="id_kategori_jasa")
    nominal = serializers.DecimalField(
        source="jumlah_pinjaman", max_digits=18, decimal_places=2
    )  # alias ke Flutter
    cicilan = serializers.DecimalField(
        source="angsuran_per_bulan", max_digits=18, decimal_places=2
    )
    jasa = serializers.DecimalField(
        source="jasa_rupiah", max_digits=18, decimal_places=2, required=False
    )

    class Meta:
        model = Pinjaman
        fields = [
            "id_pinjaman", "nomor_anggota", "id_admin",
            "jenis_pinjaman", "kategori_jasa", "nominal",
            "cicilan", "jasa", "tanggal_meminjam",
            "jatuh_tempo", "sisa_pinjaman", "status"
        ]

class AngsuranSerializer(serializers.ModelSerializer):
    id_pinjaman = serializers.PrimaryKeyRelatedField(read_only=True)
    id_admin = serializers.StringRelatedField()

    class Meta:
        model = Angsuran
        fields = ["id_pembayaran", "id_pinjaman", "id_admin", "jumlah_bayar", "tanggal_bayar"]