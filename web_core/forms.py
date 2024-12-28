from django.forms import ModelForm, DateInput, ValidationError, DateField
from .models import *

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
    def clean(self):
        benhnhan = BENHNHAN.objects.filter(
            ho_ten=self.cleaned_data.get("ho_ten"),
            ngay_sinh=self.cleaned_data.get("ngay_sinh"),
            gioi_tinh=self.cleaned_data.get("gioi_tinh"),
            dia_chi=self.cleaned_data.get("dia_chi"),
            )
        if benhnhan.exists():
            raise ValidationError("Bệnh nhân đã tồn tại")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["id"].widget.attrs["readonly"] = True

class phieukham_form(ModelForm):
    class Meta:
        model = PHIEUKHAM
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["id"].widget.attrs["readonly"] = True

class sudungthuoc_form(ModelForm):
    class Meta:
        model = SUDUNGTHUOC
        fields = '__all__'

class ThayDoiGiaTriForm(ModelForm):
    class Meta:
        model = THAMSO
        fields = ['now_value']

class DanhMucForm(ModelForm):
    class Meta:
        model = DANHMUC
        fields = ['ten']

class ThuocForm(ModelForm):
    class Meta:
        model = DANHMUC
        fields = ['ten', 'gia_tri']

from django.contrib.auth.models import User
from django import forms

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

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Mật khẩu và xác nhận mật khẩu không khớp.")

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'date': 'Ngày khám',
            'time': 'Giờ khám',
            'reason': 'Lý do khám',
        }
