# Generated by Django 2.2.1 on 2019-07-09 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0003_auto_20190707_2212'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asin', models.CharField(max_length=20)),
                ('update_date', models.CharField(max_length=200)),
                ('product_name', models.CharField(max_length=200)),
                ('product_rating', models.CharField(max_length=200)),
                ('product_review_cnt', models.IntegerField(default=0)),
                ('product_price', models.CharField(max_length=200)),
                ('product_image_url', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='insight',
            name='insight_seq',
            field=models.IntegerField(default=0),
        ),
    ]
