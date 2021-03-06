# Generated by Django 2.2.1 on 2019-06-27 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AmazonReviews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asin', models.CharField(max_length=200)),
                ('reviewer_name', models.CharField(max_length=200)),
                ('reviewer_id', models.CharField(max_length=200)),
                ('review_date', models.CharField(max_length=200)),
                ('review_title', models.CharField(max_length=200)),
                ('review_helpful', models.CharField(max_length=200)),
                ('review_rating', models.CharField(max_length=200)),
                ('review_text', models.CharField(max_length=2000)),
            ],
        ),
    ]
