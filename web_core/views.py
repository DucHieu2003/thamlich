from django.shortcuts import render, redirect

#models import
from .models import *

#authentication import
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import Group

from django.contrib.auth.decorators import login_required, permission_required
from .decorators import admin_only

#utils
from datetime import datetime as dt
from django.db.models import Count, Sum, F

#forms import
from .forms import benhnhan_form, phieukham_form, ThayDoiGiaTriForm, DanhMucForm, ThuocForm
from django.forms import inlineformset_factory

#filters import
from .filters import dskb_filter, baocao_filter, LichSuKhamFilter

from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import AppointmentForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.utils.timezone import now

# Create your views here.

# Kiểm tra quyền admin hoặc lễ tân
def admin_or_receptionist(user):
    return user.groups.filter(name__in=['admin', 'receptionist']).exists()


# Helper: Kiểm tra lịch hẹn của user hoặc admin
def get_appointments_by_role(user):
    if user.groups.filter(name='admin').exists():
        return Appointment.objects.all()
    return Appointment.objects.filter(user=user)


# Authentication
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Username or password was incorrect')
    return render(request, 'web_core/login.html')

def logoutUser(request):
    logout(request)
    return redirect('login')

# Home
def home(request):
    return render(request, 'web_core/dashboard.html')

# Danh sách bệnh nhân
@login_required(login_url='login')
def dskb(request):
    if not request.user.groups.filter(name__in=['admin', 'customer']).exists():
        return HttpResponseForbidden("Bạn không có quyền truy cập vào trang này.")
    
    max_benhnhan = THAMSO.objects.filter(loai='Số lượng bệnh nhân tối đa').first().now_value if THAMSO.objects.filter(loai='Số lượng bệnh nhân tối đa').exists() else 40
    today = dt.today().date()
    form = dskb_filter(request.POST or None)
    if form.is_valid() and form.cleaned_data.get('ngay_kham'):
        today = dt.strptime(form.cleaned_data['ngay_kham'], '%d/%m/%Y').date()
    phieukhams = PHIEUKHAM.objects.filter(ngay_kham__date=today)
    benhnhans = [BENHNHAN.objects.get(id=phieukham.id_benhnhan.id) for phieukham in phieukhams]
    context = {
        'enum_dskb': enumerate(benhnhans, start=1),
        'count': len(phieukhams),
        'max_benhnhan': max_benhnhan,
        'today': today.strftime('%d/%m/%Y'),
        'form': form,
    }
    return render(request, 'web_core/dskb.html', context)

@admin_only
def dsbn(request):
    dsbn = BENHNHAN.objects.all()
    context = {'dsbn': dsbn}
    return render(request, 'web_core/dsbn.html', context)

@admin_only
def add_benhnhan(request):
    form = benhnhan_form(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/dskb')
    return render(request, 'web_core/add_benhnhan.html', {'form': form})

@admin_only
def edit_benhnhan(request, id):
    benhnhan = BENHNHAN.objects.get(id=id)
    form = benhnhan_form(request.POST or None, instance=benhnhan)
    if form.is_valid():
        form.save()
        return redirect('/dsbn')
    return render(request, 'web_core/edit_benhnhan.html', {'form': form})

@admin_only
def del_benhnhan(request, id):
    benhnhan = BENHNHAN.objects.get(id=id)
    if request.method == 'POST':
        benhnhan.delete()
        return redirect('/dsbn')
    return render(request, 'web_core/del_benhnhan.html', {'benhnhan': benhnhan})

@login_required(login_url='login')
def xuathoadon(request):
    phieukhams = PHIEUKHAM.objects.all()
    enum_xhd = enumerate(phieukhams,start = 1)
    context = {'phieukhams':phieukhams, 'enum_xhd':enum_xhd}
    return render(request, 'web_core/xuathoadon.html', context)

@login_required(login_url='login')
def hoadon(request, pk):
    phieukham = PHIEUKHAM.objects.get(id=pk)
    tienkham = THAMSO.objects.get(loai='Tiền khám').now_value
    sdthuocs = SUDUNGTHUOC.objects.filter(id_phieukham=phieukham)  
    enum_dsthuoc = enumerate(sdthuocs,start = 1) 
    tienthuoc = 0
    for sdthuoc in sdthuocs:
        tienthuoc += sdthuoc.soluong * sdthuoc.thuoc.gia_tri
    tong = tienkham + tienthuoc
    context = {'phieukham':phieukham, 'tienkham':tienkham, 'tienthuoc':tienthuoc, 'tongtien':tong, 'enum_dsthuoc':enum_dsthuoc}
    return render(request, 'web_core/hoadon.html', context)

@login_required(login_url='login')
def lsk(request):
    lsk = PHIEUKHAM.objects.all().order_by('ngay_kham')
    enum_lsk = enumerate(lsk, start = 1)
    myFilter = LichSuKhamFilter()
    if request.GET.__contains__('ID'):
        myFilter = LichSuKhamFilter(request.GET,queryset=lsk)
        lsk = myFilter.qs
        enum_lsk = enumerate(lsk, start = 1)

    context ={'lsk': lsk, 'myFilter':myFilter, 'enum_lsk': enum_lsk}
    return render(request, 'web_core/lsk.html',context)

def lsk_guest(request):
    lsk_guest = None
    myFilter = LichSuKhamFilter()
    enum_lsk_guest = None
    if request.method == 'GET' and 'ID' in request.GET:
        ID = request.GET['ID']
        if ID :
            lsk_guest = PHIEUKHAM.objects.all().order_by('ngay_kham')
            myFilter = LichSuKhamFilter(request.GET,queryset=lsk_guest)
            lsk_guest = myFilter.qs
            enum_lsk_guest = enumerate(lsk_guest, start = 1)
        else:
            lsk_guest = None
        
    context ={'lsk_guest': lsk_guest, 'myFilter':myFilter,'enum_lsk_guest':enum_lsk_guest}
    return render(request, 'web_core/lsk_guest.html',context)
@login_required(login_url='login')
def dspk(request):
    dspk = PHIEUKHAM.objects.all().order_by('-ngay_kham')
    enum_dspk = enumerate(dspk,start = 1)

    context = {'enum_dspk':enum_dspk}
    return render(request, 'web_core/dspk.html', context)

@login_required(login_url='login')
def view_phieukham(request, id):
    phieukham = PHIEUKHAM.objects.get(id=id)
    sdt = SUDUNGTHUOC.objects.filter(id_phieukham = id)
    enum_dsthuoc = enumerate(sdt,start = 1)
    context = {'phieukham':phieukham, 'enum_dsthuoc':enum_dsthuoc}
    return render(request,'web_core/view_phieukham.html', context)

@login_required(login_url='login')
def add_phieukham(request):
    sdtFormSet = inlineformset_factory(PHIEUKHAM, SUDUNGTHUOC, 
                 fields=('id_phieukham','thuoc', 'soluong', 'don_vi', 'cach_dung'), extra=10)
    pk_form = phieukham_form()
    formset = sdtFormSet()
    if request.method == 'POST':
        print(request.POST)
        pk_form = phieukham_form(request.POST)
        if pk_form.is_valid():
            pk_form.save()
        pk = PHIEUKHAM.objects.get(id = pk_form['id'].data)
        formset = sdtFormSet(request.POST, instance=pk)
        if formset.is_valid():
            formset.save()
            return redirect('/dspk')
    context = {'pk_form':pk_form, 'formset':formset}
    return render(request,'web_core/add_phieukham.html', context)

@admin_only
def edit_phieukham(request, id):
    sdtFormSet = inlineformset_factory(PHIEUKHAM, SUDUNGTHUOC, 
                 fields=('id_phieukham','thuoc', 'soluong', 'don_vi', 'cach_dung'), extra=10)
    phieukham = PHIEUKHAM.objects.get(id=id)
    pk_form = phieukham_form(instance=phieukham)
    formset = sdtFormSet(instance=phieukham)
    if request.method == 'POST':
        pk_form = phieukham_form(request.POST, instance=phieukham)
        if pk_form.is_valid():
            pk_form.save()
        formset = sdtFormSet(request.POST, instance=phieukham)
        if formset.is_valid():
            formset.save()
            return redirect('/dspk')
    context = {'pk_form':pk_form, 'formset':formset}
    return render(request,'web_core/edit_phieukham.html', context)

@admin_only
def del_phieukham(request, id):
    phieukham = PHIEUKHAM.objects.get(id=id)
    if request.method == 'POST':
        phieukham.delete()
        return redirect('/dspk')
    context = {'phieukham':phieukham}
    return render(request,'web_core/del_phieukham.html', context)

@admin_only
def lap_bao_cao(request):
    return render(request, 'web_core/lapbaocao.html')

@admin_only
def baocao_doanhthuthang(request):
    thang_nam = dt.today().date()
    form = baocao_filter
    if request.method == 'POST':
        form = baocao_filter(request.POST)
        if form.is_valid() and form['thang_bao_cao'].data != "":
            thang_nam = dt.strptime(form['thang_bao_cao'].data, '%m/%Y')

    queryset_dict_ngay = PHIEUKHAM.objects.values('ngay_kham').filter(ngay_kham__month=thang_nam.month).filter(ngay_kham__year=thang_nam.year)
    ngay = []
    so_benh_nhan = []
    doanh_thu = []

    for dict_ngay in queryset_dict_ngay:
        # print(dict_ngay['ngay_kham'].strftime('%d/%m/%Y'))
        ngay_kham = dict_ngay['ngay_kham'].date()
        if len(ngay) > 0 and ngay_kham == ngay[-1]:
            continue

        ngay.append(ngay_kham)
        phieukham_ngay = PHIEUKHAM.objects.filter(ngay_kham__date=ngay_kham)
        so_benh_nhan.append(phieukham_ngay.count())
        doanh_thu_ngay = 0

        for phieu in phieukham_ngay:
            sdthuocs = SUDUNGTHUOC.objects.filter(id_phieukham=phieu.id)
            print(sdthuocs)
            for sdthuoc in sdthuocs:
                doanh_thu_ngay += sdthuoc.soluong * sdthuoc.thuoc.gia_tri

        doanh_thu_ngay += so_benh_nhan[-1] * THAMSO.objects.get(loai='Tiền khám').now_value
        doanh_thu.append(doanh_thu_ngay)

    ty_le = [round(100 * x / sum(doanh_thu), 2) for x in doanh_thu]
    stt = [x for x in range(len(ngay))]

    context = {'thang': thang_nam.strftime('%m/%Y'), 'stt': stt, 'ngay': ngay, 'so_benh_nhan': so_benh_nhan, 'doanh_thu': doanh_thu,
               'ty_le': ty_le, 'form': form}
    return render(request, 'web_core/baocaodoanhthuthang.html', context=context)

@admin_only
def baocao_sudungthuoc(request):
    thang_nam = dt.today().date()
    form = baocao_filter
    if request.method == 'POST':
        form = baocao_filter(request.POST)
        if form.is_valid() and form['thang_bao_cao'].data != "":
            thang_nam = dt.strptime(form['thang_bao_cao'].data, '%m/%Y')

    queryset_ngay = PHIEUKHAM.objects.filter(ngay_kham__month=thang_nam.month).filter(ngay_kham__year=thang_nam.year).values_list('id', flat=True)
    sdthuoc = SUDUNGTHUOC.objects.filter(id_phieukham__in=queryset_ngay)

    rows = (sdthuoc
            .values('thuoc', 'don_vi')
            .annotate(ten_thuoc = F('thuoc__ten'))
            .annotate(ten_donvi = F('don_vi__ten'))
            .annotate(so_luong=Sum('soluong'))
            .annotate(so_lan_dung=Count('thuoc'))
            .order_by()
            )

    stt = [x for x in range(len(rows))]
    context = {'thang': thang_nam.strftime('%m/%Y'), 'stt': stt, 'rows': rows, 'form': form}
    return render(request, 'web_core/baocaosudungthuoc.html', context=context)

@admin_only
def thaydoi_quydinh(request):
    return render(request, 'web_core/thaydoiquydinh.html')

@admin_only
def thaydoi_slbn(request):
    slbn = THAMSO.objects.get(loai='Số lượng bệnh nhân tối đa')
    form = ThayDoiGiaTriForm(initial={'loai': slbn, 'now_value': slbn.now_value})

    if request.method == 'POST':
        form = ThayDoiGiaTriForm(request.POST, instance=slbn)
        if form.is_valid():
            form.save()
            return redirect('/thaydoi')

    context = {'form': form}
    return render(request, 'web_core/thaydoi_slbn.html', context)

@admin_only
def thaydoi_tienkham(request):
    tien_kham = THAMSO.objects.get(loai='Tiền khám')
    form = ThayDoiGiaTriForm(initial={'loai': tien_kham, 'now_value': tien_kham.now_value})

    if request.method == 'POST':
        form = ThayDoiGiaTriForm(request.POST, instance=tien_kham)
        if form.is_valid():
            form.save()
            return redirect('/thaydoi')

    context = {'form': form}
    return render(request, 'web_core/thaydoi_tienkham.html', context)

@admin_only
def thaydoi_loaibenh(request):
    dslb = DANHMUC.objects.filter(loai='Bệnh')
    context = {'dslb': dslb}
    return render(request, 'web_core/thaydoi_loaibenh.html', context)

@admin_only
def thaydoi_loaibenh_them(request):
    benh = DANHMUC(loai='Bệnh')
    form = DanhMucForm()

    if request.method == 'POST':
        form = DanhMucForm(request.POST, instance=benh)
        if form.is_valid():
            form.save()
            return redirect('/thaydoi/loaibenh')

    context = {'form': form}
    return render(request, 'web_core/thaydoi_loaibenh_them.html', context)

@admin_only
def thaydoi_loaibenh_xoa(request, id):
    benh = DANHMUC.objects.get(id=id)

    if request.method == 'POST':
        benh.delete()
        return redirect('/thaydoi/loaibenh')

    context = {'benh': benh}
    return render(request, 'web_core/thaydoi_loaibenh_xoa.html', context)

@admin_only
def thaydoi_dvt(request):
    dsdvt = DANHMUC.objects.filter(loai='Đơn vị')
    context = {'dsdvt': dsdvt}
    return render(request, 'web_core/thaydoi_dvt.html', context)

@admin_only
def thaydoi_dvt_them(request):
    dvt = DANHMUC(loai='Đơn vị')
    form = DanhMucForm()

    if request.method == 'POST':
        form = DanhMucForm(request.POST, instance=dvt)
        if form.is_valid():
            form.save()
            return redirect('/thaydoi/donvitinh')

    context = {'form': form}
    return render(request, 'web_core/thaydoi_dvt_them.html', context)

@admin_only
def thaydoi_dvt_xoa(request, id):
    dvt = DANHMUC.objects.get(id=id)

    if request.method == 'POST':
        dvt.delete()
        return redirect('/thaydoi/donvitinh')

    context = {'dvt': dvt}
    return render(request, 'web_core/thaydoi_dvt_xoa.html', context)

@admin_only
def thaydoi_cachdung(request):
    ds_cach_dung = DANHMUC.objects.filter(loai='Cách dùng')
    context = {'ds_cach_dung': ds_cach_dung}
    return render(request, 'web_core/thaydoi_cachdung.html', context)

@admin_only
def thaydoi_cachdung_them(request):
    cach_dung = DANHMUC(loai='Cách dùng')
    form = DanhMucForm()

    if request.method == 'POST':
        form = DanhMucForm(request.POST, instance=cach_dung)
        if form.is_valid():
            form.save()
            return redirect('/thaydoi/cachdung')

    context = {'form': form}
    return render(request, 'web_core/thaydoi_cachdung_them.html', context)

@admin_only
def thaydoi_cachdung_xoa(request, id):
    cach_dung = DANHMUC.objects.get(id=id)

    if request.method == 'POST':
        cach_dung.delete()
        return redirect('/thaydoi/cachdung')

    context = {'cach_dung': cach_dung}
    return render(request, 'web_core/thaydoi_cachdung_xoa.html', context)

@admin_only
def thaydoi_thuoc(request):
    ds_thuoc = DANHMUC.objects.filter(loai='Thuốc')
    context = {'ds_thuoc': ds_thuoc}
    return render(request, 'web_core/thaydoi_thuoc.html', context)

@admin_only
def thaydoi_thuoc_them(request):
    thuoc = DANHMUC(loai='Thuốc')
    form = ThuocForm()

    if request.method == 'POST':
        form = ThuocForm(request.POST, instance=thuoc)
        if form.is_valid():
            form.save()
            return redirect('/thaydoi/thuoc')

    context = {'form': form}
    return render(request, 'web_core/thaydoi_thuoc_them.html', context)

@admin_only
def thaydoi_thuoc_xoa(request, id):
    thuoc = DANHMUC.objects.get(id=id)

    if request.method == 'POST':
        thuoc.delete()
        return redirect('/thaydoi/thuoc')

    context = {'thuoc': thuoc}
    return render(request, 'web_core/thaydoi_thuoc_xoa.html', context)

@admin_only
def thaydoi_thuoc_sua(request, id):
    thuoc = DANHMUC.objects.get(id=id)
    form = ThuocForm(instance=thuoc, initial={'ten': thuoc.ten, 'gia_tri': thuoc.gia_tri})

    if request.method == 'POST':
        form = ThuocForm(request.POST, instance=thuoc)
        if form.is_valid():
            form.save()
            return redirect('/thaydoi/thuoc')

    context = {'ten_thuoc': thuoc.ten, 'form': form}
    return render(request, 'web_core/thaydoi_thuoc_sua.html', context)

def registerPage(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Lưu người dùng mới
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Gán người dùng vào nhóm 'guest'
            guest_group = Group.objects.get(name='guest')  # Lấy nhóm 'guest'
            user.groups.add(guest_group)  # Gán người dùng vào nhóm 'guest'

            # Tự động đăng nhập sau khi đăng ký
            login(request, user)
            messages.success(request, "Tài khoản đã được tạo thành công với vai trò Guest!")
            return redirect('home')  # Điều hướng về trang chủ
    else:
        form = RegisterForm()

    context = {'form': form}
    return render(request, 'web_core/register.html', context)

@login_required(login_url='login')
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, "Lịch khám đã được đăng ký thành công!")
            return redirect('home')  
    else:
        form = AppointmentForm()
    return render(request, 'web_core/book_appointment.html', {'form': form})

@login_required(login_url='login')
def view_appointments(request):
    # Kiểm tra nhóm người dùng
    user_group = request.user.groups.first()


    if user_group and user_group.name == 'admin':
        appointments = Appointment.objects.all()

    
    elif user_group and user_group.name == 'customer':
        appointments = Appointment.objects.all()

    # Nếu là guest, chỉ lấy lịch của chính họ
    else:
        appointments = Appointment.objects.filter(user=request.user)

    context = {'appointments': appointments}
    return render(request, 'web_core/view_appointments.html', context)

@login_required
def delete_appointment(request, pk):
    appointment = Appointment.objects.filter(id=pk).first()
    if appointment:
        appointment.delete()
        messages.success(request, "Lịch hẹn đã được xóa thành công.")
    else:
        messages.error(request, "Không tìm thấy lịch hẹn.")
    return redirect('view_appointments')

@login_required
def update_appointment(request, pk):
    # Lấy lịch khám theo ID và đảm bảo lịch thuộc về người dùng hiện tại
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Lịch khám đã được cập nhật thành công!")
            return redirect('view_appointments')  # Điều hướng về danh sách lịch khám
    else:
        form = AppointmentForm(instance=appointment)

    # Hiển thị form cập nhật
    context = {'form': form, 'appointment': appointment}
    return render(request, 'web_core/update_appointment.html', context)



# Thêm bệnh nhân từ lịch hẹn
@login_required(login_url='login')
def add_patient_from_appointment(request):
    # Chỉ cho phép admin hoặc lễ tân thực hiện
    if not admin_or_receptionist(request.user):
        return HttpResponseForbidden("Bạn không có quyền truy cập chức năng này.")
    
    # Lọc ra các lịch hẹn của khách vãng lai (guest) chưa được xử lý
    appointments = Appointment.objects.filter(user__groups__name='guest', status='pending')

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_appointments')
        
        for appointment_id in selected_ids:
            appointment = get_object_or_404(Appointment, id=appointment_id)
            
            # Kiểm tra bệnh nhân đã tồn tại dựa trên thông tin lịch hẹn
            benhnhan_exists = BENHNHAN.objects.filter(
                ho_ten=appointment.name,
                ngay_sinh=appointment.date_of_birth
            ).exists()

            if not benhnhan_exists:
                BENHNHAN.objects.create(
                    ho_ten=appointment.name,
                    ngay_sinh=appointment.date_of_birth,
                    gioi_tinh="Chưa cập nhật",
                    dia_chi="Chưa cập nhật",
                    appointment=appointment  # Gắn lịch hẹn với bệnh nhân
                )
                # Đánh dấu lịch hẹn là hoàn thành
                appointment.status = 'completed'
                appointment.save()
            else:
                messages.warning(request, f"Bệnh nhân {appointment.name} đã tồn tại trong hệ thống.")
        
        messages.success(request, "Bệnh nhân đã được thêm vào danh sách.")
        return redirect('dskb')

    return render(request, 'web_core/add_patient_from_appointment.html', {'appointments': appointments})

# @login_required(login_url='login')
# @permission_required('myapp.manage_roles', raise_exception=True)
# def role_list(request):
#     roles = Role.objects.all()
#     return render(request, 'web_core/role_list.html', {'roles': roles})


# Hàm kiểm tra vai trò Admin
def is_admin(user):
    return user.is_superuser or UserRole.objects.filter(user=user, role__name='Admin').exists()


# Danh sách vai trò
@login_required(login_url='login')
def role_list(request):
    if not is_admin(request.user):
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('home')

    roles = Role.objects.all()
    return render(request, 'web_core/role_list.html', {'roles': roles})


# Thêm vai trò
@login_required(login_url='login')
def add_role(request):
    if not is_admin(request.user):
        messages.error(request, 'Bạn không có quyền thêm vai trò.')
        return redirect('role_list')

    if request.method == 'POST':
        role_name = request.POST['role_name']
        Role.objects.create(name=role_name)
        messages.success(request, 'Vai trò mới đã được thêm.')
        return redirect('role_list')

    return render(request, 'web_core/add_role.html')


# Chỉnh sửa vai trò
@login_required(login_url='login')
def edit_role(request, id):
    if not is_admin(request.user):
        messages.error(request, 'Bạn không có quyền chỉnh sửa vai trò.')
        return redirect('role_list')

    role = get_object_or_404(Role, id=id)
    if request.method == 'POST':
        role.name = request.POST['role_name']
        role.save()
        messages.success(request, 'Vai trò đã được cập nhật.')
        return redirect('role_list')

    return render(request, 'web_core/edit_role.html', {'role': role})


# Xóa vai trò
@login_required(login_url='login')
def delete_role(request, id):
    if not is_admin(request.user):
        messages.error(request, 'Bạn không có quyền xóa vai trò.')
        return redirect('role_list')

    role = get_object_or_404(Role, id=id)
    if UserRole.objects.filter(role=role).exists():
        messages.warning(request, 'Không thể xóa vai trò đang được gán cho người dùng.')
    else:
        role.delete()
        messages.success(request, 'Vai trò đã được xóa.')
    return redirect('role_list')


# Gán vai trò cho người dùng
@login_required(login_url='login')
def assign_role(request, user_id):
    if not is_admin(request.user):
        messages.error(request, 'Bạn không có quyền gán vai trò.')
        return redirect('user_list')

    user = get_object_or_404(User, id=user_id)
    roles = Role.objects.all()

    if request.method == 'POST':
        role_id = request.POST['role']
        role = Role.objects.get(id=role_id)
        UserRole.objects.update_or_create(user=user, defaults={'role': role})
        messages.success(request, f'Vai trò "{role.name}" đã được gán cho {user.username}.')
        return redirect('user_list')

    return render(request, 'web_core/assign_role.html', {'user': user, 'roles': roles})


# Danh sách người dùng
@login_required(login_url='login')
def user_list(request):
    users = User.objects.all()
    return render(request, 'web_core/user_list.html', {'users': users})


# Quản lý quyền của người dùng
@login_required(login_url='login')
def manage_user_permissions(request, user_id):
    if not is_admin(request.user):
        messages.error(request, 'Bạn không có quyền quản lý quyền của người dùng.')
        return redirect('user_list')

    user = get_object_or_404(User, id=user_id)
    permissions = Permission.objects.all()

    if request.method == 'POST':
        selected_permissions = request.POST.getlist('permissions')
        user.user_permissions.set(selected_permissions)
        messages.success(request, 'Quyền của người dùng đã được cập nhật.')
        return redirect('user_list')

    return render(request, 'web_core/manage_user_permissions.html', {'user': user, 'permissions': permissions})


# Quản lý quyền tổng thể (Cấp quyền trực tiếp cho chính mình)
@login_required
def manage_permissions(request):
    if not is_admin(request.user):
        messages.error(request, 'Bạn không có quyền quản lý quyền.')
        return redirect('home')

    permissions = Permission.objects.all()

    if request.method == 'POST':
        selected_permissions = request.POST.getlist('permissions')
        
        # Thêm quyền mới
        for perm_id in selected_permissions:
            perm = Permission.objects.get(id=perm_id)
            request.user.user_permissions.add(perm)
        
        messages.success(request, 'Quyền đã được cập nhật thành công.')
        return redirect('manage_permissions')

    context = {
        'permissions': permissions,
        'user_permissions': request.user.user_permissions.all()
    }
    return render(request, 'web_core/manage_permissions.html', context)
