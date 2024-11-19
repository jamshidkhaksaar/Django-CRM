from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('symbol', models.CharField(max_length=5)),
                ('exchange_rate', models.DecimalField(decimal_places=4, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('is_default', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Currencies',
            },
        ),
    ] 