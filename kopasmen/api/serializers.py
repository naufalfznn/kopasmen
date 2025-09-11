from rest_framework import serializers
from anggota.models import Anggota

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
