# Generated by Django 5.1.2 on 2024-11-04 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('book_id', models.AutoField(primary_key=True, serialize=False)),
                ('edition', models.CharField(max_length=80)),
                ('borrowermemno', models.IntegerField(blank=True, null=True)),
                ('borrowduedate', models.DateField(blank=True, null=True)),
                ('callnumber', models.CharField(max_length=40)),
            ],
        ),
    ]
