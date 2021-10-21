# Generated by Django 3.2.5 on 2021-10-20 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0008_inventory_ipaddress'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlaybookStatus',
            fields=[
                ('commandid', models.AutoField(primary_key=True, serialize=False)),
                ('command', models.CharField(max_length=1024)),
                ('processid', models.IntegerField()),
                ('starttiming', models.DateTimeField(null=True)),
                ('endtiming', models.DateTimeField(null=True)),
                ('playbookprogress', models.BooleanField(default=True)),
                ('playbookstatus', models.IntegerField(choices=[(0, 'Succeed'), (1, 'Failed'), (2, 'Cancel')])),
            ],
        ),
    ]
