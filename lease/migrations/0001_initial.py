# Generated by Django 4.2 on 2024-12-04 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LeaseManagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(blank=True, max_length=50, unique=True)),
                ('tenant_name', models.CharField(max_length=150)),
                ('tenant_shared_id', models.CharField(max_length=20)),
                ('unit_address', models.CharField(max_length=100)),
                ('unit_unique_id', models.CharField(max_length=50)),
                ('rent_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('term_lease', models.IntegerField(default=3)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='LeaseSpecificationSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term_lease', models.IntegerField(default=3)),
                ('state_lease', models.CharField(max_length=50)),
                ('caution_fee', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]
