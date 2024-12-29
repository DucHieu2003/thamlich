from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from web_core.models import Appointment, UserProfile

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Tạo nhóm
        groups = ['guest', 'customer', 'receptionist', 'dentist', 'admin']

        for group in groups:
            Group.objects.get_or_create(name=group)
        
        # Lấy nhóm
        guest = Group.objects.get(name='guest')
        customer = Group.objects.get(name='customer')
        receptionist = Group.objects.get(name='receptionist')
        dentist = Group.objects.get(name='dentist')
        admin = Group.objects.get(name='admin')
        
        # Gán quyền cho khách vãng lai
        guest.permissions.set([
            Permission.objects.get(codename='view_service'),
            Permission.objects.get(codename='search_service'),
        ])

        # Quyền cho bệnh nhân
        customer.permissions.set([
            Permission.objects.get(codename='add_appointment'),
            Permission.objects.get(codename='change_appointment'),
            Permission.objects.get(codename='delete_appointment'),
            Permission.objects.get(codename='view_appointment'),
            Permission.objects.get(codename='view_medicalrecord'),
            Permission.objects.get(codename='change_medicalrecord'),
            Permission.objects.get(codename='make_payment'),
        ])

        # Quyền cho lễ tân
        receptionist.permissions.set([
            Permission.objects.get(codename='add_appointment'),
            Permission.objects.get(codename='change_appointment'),
            Permission.objects.get(codename='delete_appointment'),
            Permission.objects.get(codename='view_appointment'),
            Permission.objects.get(codename='add_medicalrecord'),
            Permission.objects.get(codename='change_medicalrecord'),
            Permission.objects.get(codename='delete_medicalrecord'),
            Permission.objects.get(codename='send_notification'),
        ])

        # Quyền cho nha sĩ
        dentist.permissions.set([
            Permission.objects.get(codename='view_appointment'),
            Permission.objects.get(codename='add_treatmentplan'),
            Permission.objects.get(codename='change_medicalrecord'),
        ])

        # Quyền cho admin
        admin.permissions.set([
            Permission.objects.all()
        ])

        self.stdout.write("Quyền đã được gán thành công.")
