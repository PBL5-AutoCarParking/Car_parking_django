# Generated by Django 4.1.5 on 2023-04-25 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_cashier',
        ),
    ]
