# Generated by Django 4.2.17 on 2025-01-11 21:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('hashed_password', models.CharField(max_length=255)),
                ('nif', models.CharField(max_length=20, unique=True, verbose_name='NIF')),
                ('phone', models.CharField(max_length=20, unique=True)),
                ('full_address', models.CharField(max_length=160)),
                ('postal_code', models.CharField(max_length=8)),
                ('city', models.CharField(max_length=100)),
                ('utp', models.CharField(choices=[('C', 'Client'), ('F', 'Employee')], default='C', max_length=1)),
                ('social_security', models.IntegerField(null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
            ],
            options={
                'db_table': 'hr.users',
            },
        ),
        migrations.CreateModel(
            name='AccPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('perm_description', models.CharField(max_length=100)),
                ('perm_level', models.IntegerField(choices=[(1, 'Administrator'), (2, 'Manager'), (3, 'Employee'), (444, 'None')])),
            ],
            options={
                'db_table': 'sec.acc_permission',
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('action_type', models.CharField(choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete'), ('OTHER', 'Other')], max_length=50)),
                ('table_name', models.CharField(blank=True, max_length=255, null=True)),
                ('row_id', models.IntegerField(blank=True, null=True)),
                ('action_timestamp', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sec.audit_log',
            },
        ),
        migrations.CreateModel(
            name='ChangeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_name', models.CharField(max_length=255)),
                ('operation_type', models.CharField(choices=[('INSERT', 'Insert'), ('UPDATE', 'Update'), ('DELETE', 'Delete')], max_length=10)),
                ('row_id', models.IntegerField()),
                ('changed_by', models.CharField(blank=True, max_length=255, null=True)),
                ('change_timestamp', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sec.change_log',
            },
        ),
        migrations.CreateModel(
            name='ErrorLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('error_message', models.TextField()),
                ('error_hint', models.CharField(blank=True, max_length=400, null=True)),
                ('error_context', models.CharField(blank=True, max_length=400, null=True)),
                ('error_timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'sec.error_log',
            },
        ),
        migrations.CreateModel(
            name='UserLoginAudit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('login_timestamp', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'sec.user_login_audit',
            },
        ),
        migrations.CreateModel(
            name='UserPasswordsDictionary',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('hashed_password', models.CharField(max_length=255)),
                ('valid_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('valid_to', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='password_histories', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sec.user_passwords_dictionary',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='users.accpermission'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
