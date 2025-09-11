from rest_framework import serializers
from anggota.models import Anggota
from simpanan.models import JenisSimpanan, Simpanan, Penarikan

class LoginSerializer(serializers.Serializer):
    nip = serializers.CharField()
    password = serializers.CharField(write_only=True)

class AnggotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anggota
        fields = ['nomor_anggota', 'nama', 'nip', 'email', 'status']

class ResetPasswordSerializer(serializers.Serializer):
    nip = serializers.CharField()
    password = serializers.CharField(write_only=True)

class JenisSimpananSerializer(serializers.ModelSerializer):
    class Meta:
        model = JenisSimpanan
        fields = ["id_jenis_simpanan", "nama_jenis"]

class SimpananSerializer(serializers.ModelSerializer):
    anggota = serializers.StringRelatedField()
    admin = serializers.StringRelatedField()
    jenis_simpanan = JenisSimpananSerializer()
    nominal = serializers.DecimalField(
        source='jumlah_menyimpan', max_digits=18, decimal_places=2
    )  # alias biar Flutter pakai 'nominal'

    class Meta:
        model = Simpanan
        fields = [
            "id_simpanan", "anggota", "admin", "jenis_simpanan",
            "tanggal_menyimpan", "tanggal_menarik", "nominal"
        ]

class PenarikanSerializer(serializers.ModelSerializer):
    anggota = serializers.StringRelatedField()
    admin = serializers.StringRelatedField()
    jenis_simpanan = JenisSimpananSerializer()
    nominal = serializers.DecimalField(
        source='jumlah_penarikan', max_digits=18, decimal_places=2
    )

    class Meta:
        model = Penarikan
        fields = [
            "id_penarikan", "anggota", "admin", "jenis_simpanan",
            "tanggal_penarikan", "nominal"
        ]
