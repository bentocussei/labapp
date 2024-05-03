# Generated by Django 5.0.4 on 2024-05-03 00:01

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Escola',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255, unique=True, verbose_name='Nome da Escola')),
                ('email', models.EmailField(max_length=255, validators=[django.core.validators.EmailValidator()], verbose_name='E-mail da Escola')),
                ('numero_salas', models.PositiveIntegerField(verbose_name='Número de Salas')),
                ('provincia', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), size=None, verbose_name='Província')),
            ],
            options={
                'ordering': ['nome'],
            },
        ),
    ]
