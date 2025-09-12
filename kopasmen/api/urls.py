from django.urls import path
from .views import (
    LoginView, CheckNIPView, ResetPasswordView,
    SimpananListView, PenarikanListView,
    PinjamanListView, AngsuranListView
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("check-nip/", CheckNIPView.as_view(), name="check_nip"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("<str:nip>/simpan/", SimpananListView.as_view(), name="simpanan-list"),
    path("<str:nip>/tarik/", PenarikanListView.as_view(), name="penarikan-list"),
    path("<str:nip>/pinjaman/", PinjamanListView.as_view(), name="pinjaman-list"),

]

