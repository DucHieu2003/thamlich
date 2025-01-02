from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, DateInput, DateField
from django.utils.timezone import now
import datetime
from .models import *
from django.contrib.auth.models import User


# Form Bệnh Nhân
class benhnhan_form(ModelForm):
    ngay_sinh = DateField(
        label='Ngày sinh',
        widget=DateInput(format="%d/%m/%Y"),
        input_formats=['%d/%m/%Y']
    )

    class Meta:
        model = BENHNHAN
        fields = '__all__'
        widgets = {
            'ngay_sinh': DateInput(format="%d/%m/%Y"),
        }

    # Kiểm tra bệnh nhân đã tồn tại
    def clean(self):
        ho_ten = self.cleaned_data.get("ho_ten")
        ngay_sinh = self.cleaned_data.get("ngay_sinh")
        
        benhnhan = BENHNHAN.objects.filter(
            ho_ten=ho_ten,
            ngay_sinh=ngay_sinh
        )
        if benhnhan.exists():
            raise ValidationError(f"Bệnh nhân {ho_ten} (Ngày sinh: {ngay_sinh}) đã tồn tại.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["id"].widget.attrs["readonly"] = True


# Form Phiếu Khám
class phieukham_form(ModelForm):
    class Meta:
        model = PHIEUKHAM
        fields = '__all__'
        widgets = {
            'trieu_chung': forms.TextInput(attrs={'class': 'form-control'}),
            'loai_benh': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.id_benhnhan:
            self.fields['id_benhnhan'].widget.attrs['readonly'] = True


# Form Sử Dụng Thuốc
class sudungthuoc_form(ModelForm):
    class Meta:
        model = SUDUNGTHUOC
        fields = '__all__'


# Form Tham Số (Thay đổi giá trị)
class ThayDoiGiaTriForm(ModelForm):
    class Meta:
        model = THAMSO
        fields = ['now_value']

    def clean_now_value(self):
        value = self.cleaned_data.get('now_value')
        if value > 100:  # Giới hạn tối đa cho bệnh nhân (Ví dụ)
            raise ValidationError("Số lượng bệnh nhân tối đa không được vượt quá 100.")
        return value


# Form Danh Mục (Kiểm tra danh mục trùng lặp)
class DanhMucForm(ModelForm):
    class Meta:
        model = DANHMUC
        fields = ['ten', 'loai']

    def clean_ten(self):
        ten = self.cleaned_data.get('ten')
        loai = self.cleaned_data.get('loai')
        
        if DANHMUC.objects.filter(ten=ten, loai=loai).exists():
            raise ValidationError(f"Danh mục '{ten}' (Loại: {loai}) đã tồn tại.")
        return ten


# Form Thuốc (Quản lý giá trị)
class ThuocForm(ModelForm):
    class Meta:
        model = DANHMUC
        fields = ['ten', 'gia_tri']


# Form Đăng ký tài khoản
class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={"placeholder": "Nhập mật khẩu"})
    )
    confirm_password = forms.CharField(
        label="Xác nhận mật khẩu",
        widget=forms.PasswordInput(attrs={"placeholder": "Nhập lại mật khẩu"})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError("Mật khẩu không khớp.")
        return confirm_password


# Form Đặt Lịch Hẹn
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['name', 'date_of_birth', 'phone_number', 'date', 'time', 'reason']
        
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên người khám'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số điện thoại'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Lý do khám (Không bắt buộc)'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < datetime.date.today():
            raise ValidationError("Ngày khám không được ở quá khứ.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if Appointment.objects.filter(date=date, time=time).exists():
            raise ValidationError("Khung giờ này đã được đặt. Vui lòng chọn thời gian khác.")
        

# Form Tạo Người Dùng và Gán Vai Trò
class UserRoleForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Nhập mật khẩu"})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Nhập lại mật khẩu"})
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        label="Vai trò",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("Mật khẩu và xác nhận mật khẩu không khớp.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Gán vai trò cho người dùng
            role = self.cleaned_data['role']
            UserRole.objects.create(user=user, role=role)
            # Gán quyền từ vai trò cho người dùng
            user.user_permissions.set(role.permissions.all())
        return user
    
class RoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Chọn Quyền"
    )

    class Meta:
        model = Role
        fields = ['name', 'permissions']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Role.objects.filter(name=name).exists():
            raise ValidationError("Vai trò này đã tồn tại.")
        return name

class DichVuForm(forms.ModelForm):

    class Meta:
        model = DichVu
        fields = ['ten_dich_vu', 'gia', 'mo_ta']
        labels = {
            'ten_dich_vu': 'Tên dịch vụ',
            'gia': 'Giá',
            'mo_ta': 'Mô tả'
        }
        

