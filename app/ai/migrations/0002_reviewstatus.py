# Generated by Django 2.2.1 on 2019-07-03 01:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asin', models.CharField(max_length=200)),
                ('scrape_date', models.CharField(max_length=200)),
            ],
        ),
    ]