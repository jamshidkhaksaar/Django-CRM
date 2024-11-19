# Generated by Django 5.0.1 on 2024-11-18 18:05

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', 'XXXX_add_currency_model'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('period', models.CharField(choices=[('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')], max_length=10)),
                ('notes', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='RecurringTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('frequency', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('next_due_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='transaction',
            name='cashier_status',
            field=models.CharField(choices=[('PAID', 'Paid'), ('UNPAID', 'Unpaid'), ('PENDING', 'Pending')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='transaction',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='accounts.currency'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='transaction',
            name='requester',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='requested_transactions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('income', 'Income'), ('expense', 'Expense'), ('advance', 'Advance')], default='expense', max_length=10),
        ),
        migrations.AddField(
            model_name='transaction',
            name='version',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=15),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['status', 'cashier_status'], name='accounts_tr_status_d792be_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['created_at'], name='accounts_tr_created_b2c597_idx'),
        ),
        migrations.AddField(
            model_name='budget',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='budget',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.currency'),
        ),
        migrations.AddField(
            model_name='budget',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.category'),
        ),
        migrations.AddField(
            model_name='recurringtransaction',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.category'),
        ),
        migrations.AddField(
            model_name='recurringtransaction',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recurringtransaction',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.currency'),
        ),
    ]