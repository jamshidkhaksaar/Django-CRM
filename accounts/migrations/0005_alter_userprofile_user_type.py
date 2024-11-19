# Generated by Django 5.0.1 on 2024-11-19 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_userprofile_user_alter_userprofile_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='user_type',
            field=models.CharField(choices=[('superadmin', 'Super Admin'), ('data_entry', 'Data Entry'), ('cashier', 'Cashier')], default='data_entry', max_length=20),
        ),
    ]