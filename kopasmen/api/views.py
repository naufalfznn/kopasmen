from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, AnggotaSerializer, ResetPasswordSerializer
from anggota.models import Anggota
from simpanan.models import Simpanan, Penarikan
from .serializers import SimpananSerializer, PenarikanSerializer



class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        nip = serializer.validated_data['nip']
        password = serializer.validated_data['password']

        try:
            anggota = Anggota.objects.get(nip=nip, status="aktif")
        except Anggota.DoesNotExist:
            return Response(
                {"error": "NIP tidak ditemukan atau akun nonaktif"},
                status=status.HTTP_404_NOT_FOUND
            )

        if anggota.check_password(password): 
            data = AnggotaSerializer(anggota).data
            return Response(
                {"message": "Login berhasil", "data": data},
                status=status.HTTP_200_OK
            )
        return Response({"error": "Password salah"}, status=status.HTTP_400_BAD_REQUEST)


class CheckNIPView(APIView):
    def post(self, request):
        nip = request.data.get("nip")
        if not nip:
            return Response({"error": "NIP wajib diisi"}, status=status.HTTP_400_BAD_REQUEST)

        exists = Anggota.objects.filter(nip=nip).exists()
        return Response({"exists": exists}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        nip = serializer.validated_data["nip"]
        new_password = serializer.validated_data["password"]

        try:
            anggota = Anggota.objects.get(nip=nip, status="aktif")
        except Anggota.DoesNotExist:
            return Response(
                {"error": "NIP tidak ditemukan atau akun nonaktif"},
                status=status.HTTP_404_NOT_FOUND
            )

        anggota.set_password(new_password)
        anggota.save()

        return Response({"message": "Password berhasil direset"}, status=status.HTTP_200_OK)
    

class SimpananListView(APIView):
    def get(self, request, nip):
        simpanan = Simpanan.objects.filter(anggota__nip=nip).order_by('-tanggal_menyimpan')
        serializer = SimpananSerializer(simpanan, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PenarikanListView(APIView):
    def get(self, request, nip):
        penarikan = Penarikan.objects.filter(anggota__nip=nip).order_by('-tanggal_penarikan')
        serializer = PenarikanSerializer(penarikan, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

