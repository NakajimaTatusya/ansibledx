# Generated by Django 3.2.4 on 2021-06-17 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0006_auto_20210617_0240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='hostname',
            field=models.CharField(max_length=15, primary_key=True, serialize=False),
        ),
    ]