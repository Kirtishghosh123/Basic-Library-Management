# Generated by Django 4.2.9 on 2024-09-15 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TOKEN', '0002_alter_borrow_return_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrow',
            name='copies_requested',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
