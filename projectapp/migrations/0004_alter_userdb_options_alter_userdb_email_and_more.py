# Generated by Django 5.1.7 on 2025-03-16 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('projectapp', '0003_otpverification'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userdb',
            options={},
        ),
        migrations.AlterField(
            model_name='userdb',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Email Address'),
        ),
        migrations.AlterField(
            model_name='userdb',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='Account Status'),
        ),
        migrations.AlterField(
            model_name='userdb',
            name='mobile_number',
            field=models.CharField(max_length=15, verbose_name='Mobile Number'),
        ),
        migrations.AddConstraint(
            model_name='userdb',
            constraint=models.UniqueConstraint(fields=('email', 'is_active'), name='unique_active_email'),
        ),
        migrations.AddConstraint(
            model_name='userdb',
            constraint=models.UniqueConstraint(fields=('mobile_number', 'is_active'), name='unique_active_mobile'),
        ),
    ]
