from django.contrib import admin
from .models import AmazonReview, Insight


class AmazonReviewAdmin(admin.ModelAdmin):
    fields = ['reviewer_id', 'reviewer_name','asin','review_rating','review_title',\
        'review_date','review_text','review_helpful']
    list_display = ('reviewer_id', 'reviewer_name','asin','review_rating','review_title',\
        'review_date','review_text','review_helpful')

class InsightAdmin(admin.ModelAdmin):
    fields = ['asin', 'update_date','insight_type', 'insight_phrase', 'insight_text']
    list_display = ('asin', 'update_date','insight_type', 'insight_phrase', 'insight_text')

# Register your models here.
admin.site.register(AmazonReview, AmazonReviewAdmin)
admin.site.register(Insight, InsightAdmin)