# Generated by Django 3.2.4 on 2021-06-16 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ipv4_addr', models.GenericIPAddressField()),
                ('hostname', models.CharField(max_length=256)),
                ('username', models.CharField(max_length=256)),
                ('password', models.CharField(max_length=256)),
            ],
        ),
    ]
