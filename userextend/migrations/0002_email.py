# Generated by Django 3.1 on 2020-08-26 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userextend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=30)),
                ('body', models.TextField()),
            ],
        ),
    ]
