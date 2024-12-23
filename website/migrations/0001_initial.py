# Generated by Django 4.2 on 2024-11-30 09:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Record",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[
                            ("income", "Income"),
                            ("expense", "Expense"),
                            ("advance", "Advance"),
                            ("balance", "Balance"),
                            ("payable", "Payable"),
                        ],
                        max_length=20,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("date", models.DateField()),
                ("description", models.TextField()),
                (
                    "reference_number",
                    models.CharField(blank=True, max_length=50, null=True, unique=True),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("pending_deputy", "Pending Deputy Director Approval"),
                            ("rejected_deputy", "Rejected by Deputy Director"),
                            (
                                "pending_executive",
                                "Pending Executive Director Approval",
                            ),
                            ("rejected_executive", "Rejected by Executive Director"),
                            ("pending_ceo", "Pending CEO Approval"),
                            ("rejected_ceo", "Rejected by CEO"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "income_source",
                    models.CharField(
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
                (
                    "income_category",
                    models.CharField(
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
                (
                    "payment_method",
                    models.CharField(
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
                (
                    "expense_category",
                    models.CharField(
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
                (
                    "expense_type",
                    models.CharField(
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
                ("vendor", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "receipt_number",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "balance_type",
                    models.CharField(
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
                ("account", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "recipient_name",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "recipient_position",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("repayment_deadline", models.DateField(blank=True, null=True)),
                (
                    "repayment_method",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "lender_name",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "lender_contact",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("due_date", models.DateField(blank=True, null=True)),
                ("is_paid", models.BooleanField(default=False)),
                (
                    "current_approval_level",
                    models.CharField(
                        choices=[
                            ("cashier", "Cashier Review"),
                            ("deputy", "Deputy Director"),
                            ("executive", "Executive Director"),
                            ("ceo", "CEO"),
                        ],
                        default="cashier",
                        max_length=50,
                    ),
                ),
                ("forwarded_to_deputy", models.BooleanField(default=False)),
                ("deputy_approved", models.BooleanField(default=False)),
                ("executive_approved", models.BooleanField(default=False)),
                ("ceo_approved", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="UserSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "theme",
                    models.CharField(
                        choices=[("light", "Light"), ("dark", "Dark")],
                        default="light",
                        max_length=10,
                    ),
                ),
                (
                    "language",
                    models.CharField(
                        choices=[("en", "English"), ("fa", "Farsi")],
                        default="en",
                        max_length=2,
                    ),
                ),
                ("notifications_enabled", models.BooleanField(default=True)),
                ("email_notifications", models.BooleanField(default=True)),
                ("items_per_page", models.IntegerField(default=10)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "User Settings",
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "profile_image",
                    models.ImageField(
                        blank=True, null=True, upload_to="profile_images/"
                    ),
                ),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("department", models.CharField(blank=True, max_length=100)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserActivity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "activity_type",
                    models.CharField(
                        choices=[
                            ("login", "Login"),
                            ("logout", "Logout"),
                            ("record_create", "Record Created"),
                            ("record_update", "Record Updated"),
                            ("record_delete", "Record Deleted"),
                            ("record_approve", "Record Approved"),
                            ("record_reject", "Record Rejected"),
                            ("profile_update", "Profile Updated"),
                        ],
                        max_length=20,
                    ),
                ),
                ("description", models.TextField()),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "record",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="website.record",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "User Activities",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="TwoFactorAuth",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("secret_key", models.CharField(max_length=32)),
                ("is_enabled", models.BooleanField(default=False)),
                ("backup_codes", models.JSONField(default=list)),
                ("last_used", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ReferenceNumber",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("prefix", models.CharField(max_length=10)),
                ("year", models.CharField(max_length=4)),
                ("month", models.CharField(max_length=2)),
                ("sequence", models.IntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "unique_together": {("prefix", "year", "month", "sequence")},
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("message", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "notification_type",
                    models.CharField(
                        choices=[
                            ("record_approval", "Record Approval"),
                            ("record_status", "Record Status Change"),
                            ("record_comment", "Record Comment"),
                            ("system", "System Notification"),
                        ],
                        default="system",
                        max_length=50,
                    ),
                ),
                (
                    "record",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="website.record",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="AdvancePayback",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("payment_date", models.DateField()),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("cash", "Cash"),
                            ("bank", "Bank Transfer"),
                            ("deduction", "Salary Deduction"),
                        ],
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("is_fully_paid", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "advance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="paybacks",
                        to="website.record",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-payment_date"],
            },
        ),
        migrations.CreateModel(
            name="RecordApproval",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "approval_level",
                    models.CharField(
                        choices=[
                            ("cashier", "Cashier"),
                            ("deputy", "Deputy Director"),
                            ("executive", "Executive Director"),
                            ("ceo", "CEO"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("pending_deputy", "Pending Deputy Director Approval"),
                            ("rejected_deputy", "Rejected by Deputy Director"),
                            (
                                "pending_executive",
                                "Pending Executive Director Approval",
                            ),
                            ("rejected_executive", "Rejected by Executive Director"),
                            ("pending_ceo", "Pending CEO Approval"),
                            ("rejected_ceo", "Rejected by CEO"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        max_length=20,
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "record",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approvals",
                        to="website.record",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
                "unique_together": {("record", "approval_level")},
            },
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(
                fields=["-created_at"], name="website_not_created_a12bd5_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(
                fields=["user", "is_read"], name="website_not_user_id_5accc9_idx"
            ),
        ),
    ]
