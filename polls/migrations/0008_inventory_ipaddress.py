# Generated by Django 3.2.5 on 2021-08-19 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0007_alter_inventory_hostname'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='ipaddress',
            field=models.CharField(max_length=15, null=True),
        ),
    ]