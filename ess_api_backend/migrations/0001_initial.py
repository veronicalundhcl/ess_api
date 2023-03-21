# Generated by Django 4.1.7 on 2023-03-21 06:36

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('img', models.TextField(null=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(null=True)),
                ('category', models.TextField(default='Uncategorized')),
                ('reviews', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('link', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('value', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(default='', max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, related_name='ess_api_backend_users', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='ess_api_backend_users', to='auth.permission')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user', models.ForeignKey(default=0, editable=False, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='ess_api_backend.user')),
                ('firstname', models.CharField(default='', max_length=50)),
                ('lastname', models.CharField(default='', max_length=50)),
                ('dob', models.DateField(null=True)),
                ('department', models.CharField(max_length=50, null=True)),
                ('role', models.CharField(default='', max_length=50)),
                ('contactnum', models.CharField(max_length=15, null=True)),
                ('address', models.CharField(max_length=100, null=True)),
                ('province', models.CharField(max_length=50, null=True)),
                ('country', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('price', models.IntegerField()),
                ('date_of_purchase', models.DateField(null=True)),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ess_api_backend.product')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ess_api_backend.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('price', models.IntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ess_api_backend.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ess_api_backend.customer')),
            ],
        ),
    ]
