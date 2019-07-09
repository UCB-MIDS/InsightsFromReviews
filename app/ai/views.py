from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from fake_useragent import UserAgent

from .models import AmazonReview, Insight
from django.db.models import Max

import random
import requests
import datetime
from .insights import insights

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'}
proxies_list = ["35.198.69.233:80","178.128.11.215:80","54.226.53.87:80"]
proxies = {'http': random.choice(proxies_list)}

# Create your views here.
def index(request):
    #request.session['query_text'] = 'wassup'
    test_review = [{"reviewText":"A true cast iron pan is super smooth.", "overall":5.0},
                   {"reviewText":"Enter the Lodge 12 inch cast iron skillet.", "overall":4.0},
                   {"reviewText":"Just wash with hot water, without soap.", "overall":3.0},
                   {"reviewText":"This was horrible.I'm used to cast iron, for sure.", "overall":1.0},
                   {"reviewText":"Only hot water and maybe salt if you need an abrasive.", "overall":2.0},
                   {"reviewText":"Oil first, heat it, then food in.I'm very disappointed.This is a great skillet, especially for the price.", "overall":1.0}]
                  

    out_json_s_pos, out_json_s_neg = insights.main(["-j", test_review])
    return render(request, 'ai/index.html')

def result(request):
    query_text = request.POST.get('query_text')
    asin_list = asin_scrape(query_text)

    last_updated_str = '0000'
    last_updated = Insight.objects.raw("SELECT id, update_date FROM ai_insight WHERE asin= %s ORDER BY update_date DESC LIMIT 1", [asin_list[0]])
    for dt in last_updated:
        last_updated_str = dt.update_date    

    context = {'last_updated_str': last_updated_str,'query_text': query_text, 'asin':asin_list[0]}

    return render(request, 'ai/result.html', context)

def update(request):
    query_text = request.POST.get('query_text')

    asin_list = asin_scrape(query_text)
    review_str = ""
    for x in range(2):
        new_review_str = review_scrape(asin_list[0],x)
        if new_review_str == "NO_SEARCH_RESULT":
            break
        else:
            review_str = review_str + new_review_str

    
    today_dt = datetime.datetime.now().strftime('%Y%m%d')

    insight = Insight(asin=asin_list[0], update_date=today_dt)
    insight.save()

    response = "Updating for the query : " + query_text + " <br> >> Product ASIN : " + str(asin_list[0])

    return HttpResponse(response)


def update_result_old(request):
    
    return HttpResponse(response)

def asin_scrape(query_text):
    url_pre = 'https://www.amazon.com/s?k='
    url_post = '&ref=nb_sb_noss_2'

    parse_text_start = '<div class="a-row a-badge-region"><span id="'
    parse_text_end = '" class="a-badge"'

    url = url_pre + query_text + url_post
    print(url)

    response = requests.get(url, headers=headers, proxies=proxies).text
    parsed_asin_list = parse_page(response, parse_text_start, parse_text_end, 'list')

    return parsed_asin_list

def review_scrape(product_asin, page_number):
    url_pre = 'https://www.amazon.com/product-reviews/'
    url_post = '/reviewerType=all_reviews&sortBy=recent&pageNumber=0/ref=cm_cr_arp_d_paging_btm_next_2?pageNumber='

    parse_text_start = 'class="a-section celwidget">'
    parse_text_end = 'Report abuse'

    url = url_pre + product_asin + url_post + str(page_number)
    print(url)
    response = requests.get(url, headers=headers, proxies=proxies).text

    parsed_review = parse_page(response, parse_text_start, parse_text_end, 'list')

    asin = product_asin
    for x in range(len(parsed_review)):
        parse_block = parsed_review[x]

        reviewer_id = parse_string(parse_block, "amzn1.account.", "/ref=cm_cr_arp_d_gw_btm")
        parse_block = trim_string(parse_block, "amzn1.account.", "/ref=cm_cr_arp_d_gw_btm")
        print (" reviewer_id ###### : " + reviewer_id)

        reviewer_name = parse_string(parse_block, '<span class="a-profile-name">', '</span></div>')
        parse_block = trim_string(parse_block, '<span class="a-profile-name">', '</span></div>')
        print (" reviewr_name ###### : " + reviewer_name)

        asin = parse_string(parse_block, 'ASIN=', '"><i data-hook=')
        parse_block = trim_string(parse_block, 'ASIN=', '"><i data-hook=')
        print (" asin ###### : " + asin)

        review_rating = parse_string(parse_block, '<span class="a-icon-alt">', '</span></i>')
        parse_block = trim_string(parse_block, '<span class="a-icon-alt">', '</span></i>')
        print (" review_rating ###### : " + review_rating)

        review_title = parse_string(parse_block, '<span class="">', '</span>')
        parse_block = trim_string(parse_block, '<span class="">', '</span>')
        print (" review_title ###### : " + review_title)

        review_date = parse_string(parse_block, 'a-color-secondary review-date">', '</span>')
        parse_block = trim_string(parse_block, 'a-color-secondary review-date">', '</span>')
        review_dt = datetime.datetime.strptime(review_date, '%B %d, %Y')
        review_date = review_dt.strftime('%Y%m%d')
        print (" review_date ###### : " + review_date)

        review_text = parse_string(parse_block, 'review-text-content"><span class="">', '</span>')
        parse_block = trim_string(parse_block, 'review-text-content"><span class="">', '</span>')
        print (" review_text ###### : " + review_text)

        review_helpful = parse_string(parse_block, 'a-color-tertiary cr-vote-text">', '</span>')
        parse_block = trim_string(parse_block, 'a-color-tertiary cr-vote-text">', '</span>')
        print (" review_helpful ###### : " + review_helpful)


        amazonReview = AmazonReview(reviewer_id=reviewer_id, reviewer_name=reviewer_name,\
            asin=asin, review_rating=review_rating, review_title=review_title,\
            review_date=review_date, review_text=review_text, review_helpful=review_helpful)
        amazonReview.save()

    return asin

def parse_page(original_text, parse_text_start, parse_text_end, string_list):
    parsed_list = []
    parsed_string = ""
    original_text_processing = ""
    if(original_text.find(parse_text_start) > 0):
        original_text_processing = original_text[original_text.find(parse_text_start)+len(parse_text_start):]

        cnt=0
        while cnt < 10:
            parsed_text = original_text_processing[:original_text_processing.find(parse_text_end)]
            
            parsed_list.append(parsed_text)
            parsed_string = parsed_string + parsed_text

            cnt += 1
            print ("###### : " + str(cnt) + " :::::: " + parsed_text[:100])

            original_text_processing = original_text_processing[original_text_processing.find(parse_text_end)+len(parse_text_end):]
            if(original_text_processing.find(parse_text_start) > 0):
                original_text_processing = original_text_processing[original_text_processing.find(parse_text_start)+len(parse_text_start):]
            else:
                break
    else:
        parsed_list = ['NO_SEARCH_RESULT']
        parsed_string = 'NO_SEARCH_RESULT'

    if string_list == 'string':
        return parsed_string
    else:
        return parsed_list


def parse_string(original_text, parse_text_start, parse_text_end):
    parsed_string = ""
    if(original_text.find(parse_text_start) > 0):
        original_text_processing = original_text[original_text.find(parse_text_start)+len(parse_text_start):]
        parsed_string = original_text_processing[:original_text_processing.find(parse_text_end)]

    else:
        parsed_string = 'NO_SEARCH_RESULT'

    return parsed_string

def trim_string(original_text, parse_text_start, parse_text_end):
    original_text_processing = original_text
    if(original_text.find(parse_text_start) > 0):
        original_text_processing = original_text[original_text.find(parse_text_start)+len(parse_text_start):]
        original_text_processing = original_text_processing[original_text_processing.find(parse_text_end)+len(parse_text_end):]
    return original_text_processing



