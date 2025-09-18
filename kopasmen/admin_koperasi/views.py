from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Admin
from .forms import LoginForm

# import model lain
from anggota.models import Anggota
from simpanan.models import Simpanan
from pinjaman.models import Pinjaman
from django.db.models import Sum

ALLOWED_ROLES = {'ketua', 'sekretaris', 'bendahara'}

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']
            try:
                admin = Admin.objects.get(username=username)
            except Admin.DoesNotExist:
                messages.error(request, "Username atau password salah.")
            else:
                if admin.role not in ALLOWED_ROLES:
                    messages.error(request, "Role tidak diperbolehkan.")
                elif admin.check_password(password):
                    request.session['admin_id'] = admin.id_admin
                    request.session['admin_username'] = admin.username
                    request.session['admin_role'] = admin.role
                    return redirect('admin_koperasi:dashboard')
                else:
                    messages.error(request, "Username atau password salah.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    request.session.flush()
    messages.info(request, "Logout berhasil.")
    return redirect('admin_koperasi:login')


def dashboard_view(request):
    if not request.session.get('admin_id'):
        return redirect('admin_koperasi:login')

    role = request.session.get('admin_role')
    username = request.session.get('admin_username')

    context = {
        'username': username,
        'role': role,
    }

    if role == 'ketua':
        jumlah_admin = Admin.objects.count()
        jumlah_anggota = Anggota.objects.count()
        jumlah_simpanan = Simpanan.objects.aggregate(total=Sum('jumlah_menyimpan'))['total'] or 0
        jumlah_pinjaman = Pinjaman.objects.aggregate(total=Sum('jumlah_pinjaman'))['total'] or 0

        context.update({
            'jumlah_admin': jumlah_admin,
            'jumlah_anggota': jumlah_anggota,
            'jumlah_simpanan': jumlah_simpanan,
            'jumlah_pinjaman': jumlah_pinjaman,
        })

        tpl = 'dashboard_ketua.html'

    elif role == 'sekretaris':
        tpl = 'dashboard_sekretaris.html'

    elif role == 'bendahara':
        tpl = 'dashboard_bendahara.html'

    return render(request, tpl, context)

