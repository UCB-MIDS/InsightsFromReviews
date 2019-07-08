import datetime

from django.db import models
from django.utils import timezone


class AmazonReview(models.Model):

    asin = models.CharField(max_length=20)
    reviewer_name = models.CharField(max_length=50)
    reviewer_id = models.CharField(max_length=50)
    review_date = models.CharField(max_length=10)
    review_title = models.CharField(max_length=200)
    review_helpful = models.CharField(max_length=20)
    review_rating = models.CharField(max_length=20)
    review_text = models.CharField(max_length=2000)

    def __str__(self):
        return self.review_title

class Insight(models.Model):

    asin = models.CharField(max_length=20)
    update_date = models.CharField(max_length=200)
    insight_type = models.CharField(max_length=200)
    insight_phrase = models.CharField(max_length=200)
    insight_text = models.CharField(max_length=2000)

    def __str__(self):
        return self.asin