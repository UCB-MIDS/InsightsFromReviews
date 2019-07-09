from django.contrib import admin
from .models import AmazonReview, Insight, AmazonProduct


class AmazonReviewAdmin(admin.ModelAdmin):
    fields = ['reviewer_id', 'reviewer_name','asin','review_rating','review_title',\
        'review_date','review_text','review_helpful']
    list_display = ('reviewer_id', 'reviewer_name','asin','review_rating','review_title',\
        'review_date','review_text','review_helpful')

class InsightAdmin(admin.ModelAdmin):
    fields = ['asin', 'update_date', 'insight_seq', 'insight_type', 'insight_phrase', 'insight_text']
    list_display = ('asin', 'update_date', 'insight_seq', 'insight_type', 'insight_phrase', 'insight_text')

class AmazonProductAdmin(admin.ModelAdmin):
    fields = ['asin', 'update_date','product_name', 'product_rating', 'product_review_cnt', 'product_price', 'product_image_url']
    list_display = ('asin', 'update_date','product_name', 'product_rating', 'product_review_cnt', 'product_price', 'product_image_url')


# Register your models here.
admin.site.register(AmazonReview, AmazonReviewAdmin)
admin.site.register(Insight, InsightAdmin)
admin.site.register(AmazonProduct, AmazonProductAdmin)