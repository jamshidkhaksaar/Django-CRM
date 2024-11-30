# Generated by Django 5.1.3 on 2024-11-27 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0003_userprofile_user_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="user_type",
        ),
        migrations.AddField(
            model_name="record",
            name="account",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="record",
            name="balance_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("opening", "Opening Balance"),
                    ("closing", "Closing Balance"),
                    ("adjustment", "Balance Adjustment"),
                    ("reconciliation", "Bank Reconciliation"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="record",
            name="expense_category",
            field=models.CharField(
                blank=True,
                choices=[
                    ("utilities", "Utilities"),
                    ("supplies", "Office Supplies"),
                    ("maintenance", "Maintenance"),
                    ("salary", "Salary Payments"),
                    ("rent", "Rent"),
                    ("equipment", "Equipment"),
                    ("transportation", "Transportation"),
                    ("other", "Other"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="record",
            name="expense_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("operational", "Operational"),
                    ("administrative", "Administrative"),
                    ("project", "Project-based"),
                    ("emergency", "Emergency"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="record",
            name="income_category",
            field=models.CharField(
                blank=True,
                choices=[
                    ("regular", "Regular Income"),
                    ("one-time", "One-time Income"),
                    ("recurring", "Recurring Income"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="record",
            name="income_source",
            field=models.CharField(
                blank=True,
                choices=[
                    ("salary", "Salary"),
                    ("investment", "Investment"),
                    ("donation", "Donation"),
                    ("grant", "Grant"),
                    ("sales", "Sales"),
                    ("service", "Service Fee"),
                    ("other", "Other"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="record",
            name="payment_method",
            field=models.CharField(
                blank=True,
                choices=[
                    ("cash", "Cash"),
                    ("bank", "Bank Transfer"),
                    ("check", "Check"),
                    ("online", "Online Payment"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="record",
            name="receipt_number",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="record",
            name="vendor",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]