# Generated by Django 4.0.4 on 2024-12-30 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_core', '0005_role_alter_benhnhan_options_alter_danhmuc_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DichVu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ten_dich_vu', models.CharField(max_length=100)),
                ('gia', models.DecimalField(decimal_places=2, max_digits=10)),
                ('mo_ta', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
