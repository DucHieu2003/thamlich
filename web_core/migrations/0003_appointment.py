# Generated by Django 4.0.4 on 2024-12-27 08:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('web_core', '0002_alter_benhnhan_id_alter_danhmuc_id_alter_danhmuc_ten_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Ngày khám')),
                ('time', models.TimeField(verbose_name='Giờ khám')),
                ('reason', models.TextField(blank=True, null=True, verbose_name='Lý do khám')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Người dùng')),
            ],
        ),
    ]