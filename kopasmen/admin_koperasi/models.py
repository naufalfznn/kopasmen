from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User

class Admin(models.Model):
    ROLE_CHOICES = [
        ('ketua', 'Ketua'),
        ('sekretaris', 'Sekretaris'),
        ('bendahara', 'Bendahara'),
    ]

    id_admin = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    user = models.OneToOneField(User, on_delete=models.CASCADE) 

    class Meta:
        db_table = 'Admin'

    def __str__(self):
        return f"Admin {self.username} ({self.get_role_display()})"

    def set_password(self, raw_password: str):
        """Menyimpan password yang sudah di-hash."""
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Memeriksa apakah password yang diberikan cocok dengan yang sudah di-hash."""
        return check_password(raw_password, self.password_hash)
