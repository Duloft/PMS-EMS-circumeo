# Generated by Django 5.1.4 on 2025-01-07 09:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_token_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 10, 9, 50, 49, 240128, tzinfo=datetime.timezone.utc)),
        ),
    ]
