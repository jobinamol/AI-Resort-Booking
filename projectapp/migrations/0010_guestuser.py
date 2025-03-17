# Generated by Django 5.1.7 on 2025-03-17 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectapp', '0009_room'),
    ]

    operations = [
        migrations.CreateModel(
            name='GuestUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email Address')),
                ('full_name', models.CharField(max_length=255, verbose_name='Full Name')),
                ('mobile_number', models.CharField(max_length=15, unique=True, verbose_name='Mobile Number')),
                ('password', models.CharField(max_length=255, verbose_name='Password')),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='guest_profiles/', verbose_name='Profile Picture')),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Account Status')),
                ('preferences', models.JSONField(blank=True, default=dict)),
            ],
            options={
                'verbose_name': 'Guest User',
                'verbose_name_plural': 'Guest Users',
                'ordering': ['-date_joined'],
            },
        ),
    ]
