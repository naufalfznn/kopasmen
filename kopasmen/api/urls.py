from django.urls import path
from .views import LoginView, CheckNIPView, ResetPasswordView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("check-nip/", CheckNIPView.as_view(), name="check_nip"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
]
