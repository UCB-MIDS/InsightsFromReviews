from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from fake_useragent import UserAgent


from .models import AmazonReview, Insight, AmazonProduct
from django.db.models import Max

import time
import random
import requests
import datetime
import ast
from .insights import insights


headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'}
#proxies_list = ["35.198.69.233:80","178.128.11.215:80","54.226.53.87:80"]
# https://www.us-proxy.org/
proxies_list = ["104.245.69.17","70.169.132.131","24.172.34.114","79.141.163.75","70.169.132.131"]
proxies = {'http': random.choice(proxies_list)}

# Create your views here.
def home(request):
    return render(request, 'ai/home.html')

def about(request):
    return render(request, 'ai/about.html')

# Create your views here.
def actionableinsight(request):
    return render(request, 'ai/actionableinsight.html')

def result(request, query_text_from_url='NO_QUERY'):
    query_text = request.POST.get('query_text')
    if (query_text_from_url != 'NO_QUERY'):
        query_text = query_text_from_url
    #asin_list = asin_scrape(query_text)
    asin_list = get_asin(query_text)
    print(query_text)


    product_asin = str(asin_list[0])
    print("FROM result - asin_list[0] :  "+str(asin_list))


    if len(asin_list) > 1:
        product_asin_2 = str(asin_list[1])
    if len(asin_list) > 2:
        product_asin_3 = str(asin_list[2])
    print ("product_asin from result() : " + product_asin)  

    # Get Product Info
    update_date = product_name =  product_image_url = product_rating = product_review_cnt = product_price = ''
    product_info = AmazonProduct.objects.raw("SELECT id, update_date, product_name, product_rating, product_review_cnt, product_price, product_image_url \
        FROM ai_amazonproduct WHERE asin= %s ORDER BY update_date DESC LIMIT 1", [product_asin])
    if len(product_info) > 0 :
        for p in product_info:
            update_date = p.update_date
            product_name = p.product_name
            product_image_url = p.product_image_url
            product_rating = p.product_rating
            product_review_cnt = p.product_review_cnt
            product_price = p.product_price
    # if no date, scrape from Amazon
    else : 
        product_name, product_image_url, product_rating, product_review_cnt, product_price, update_date = \
            scrape_product_info(product_asin)
    product_stars_url = "review_" + str(int(float(product_rating)))+".png"
    insight_positive_list = get_insights(str(product_asin), 'P')
    insight_negative_list = get_insights(str(product_asin), 'N')

    context = {'update_date': update_date,'query_text': query_text, 'asin':asin_list[0],\
        'product_name':product_name, 'product_rating':product_rating, 'product_review_cnt':product_review_cnt,\
        'insight_negative_list':insight_negative_list, 'insight_positive_list':insight_positive_list,\
        'product_price':product_price, 'product_image_url':product_image_url, 'product_stars_url':product_stars_url,\
        }

    # Get Product Info 2
    if len(asin_list) > 1:
        update_date_2 = product_name_2 =  product_image_url_2 = product_rating_2 = product_review_cnt_2 = product_price_2 = ''
        product_info_2 = AmazonProduct.objects.raw("SELECT id, update_date, product_name, product_rating, product_review_cnt, product_price, product_image_url \
            FROM ai_amazonproduct WHERE asin= %s ORDER BY update_date DESC LIMIT 1", [product_asin_2])
        if len(product_info_2) > 0 :
            for p in product_info_2:
                update_date_2 = p.update_date
                product_name_2 = p.product_name
                product_image_url_2 = p.product_image_url
                product_rating_2 = p.product_rating
                product_review_cnt_2 = p.product_review_cnt
                product_price_2 = p.product_price
        # if no date, scrape from Amazon
        else : 
            product_name_2, product_image_url_2, product_rating_2, product_review_cnt_2, product_price_2, update_date_2 = \
                scrape_product_info(product_asin_2)
        product_stars_url_2 = "review_" + str(int(float(product_rating_2)))+".png"
        insight_positive_list_2 = get_insights(str(product_asin_2), 'P')
        insight_negative_list_2 = get_insights(str(product_asin_2), 'N')

        context = {'update_date': update_date,'query_text': query_text, 'asin':asin_list[0],\
            'product_name':product_name, 'product_rating':product_rating, 'product_review_cnt':product_review_cnt,\
            'insight_negative_list':insight_negative_list, 'insight_positive_list':insight_positive_list,\
            'product_price':product_price, 'product_image_url':product_image_url, 'product_stars_url':product_stars_url,\

            'update_date_2': update_date_2, 'asin_2':product_asin_2,\
            'product_name_2':product_name_2, 'product_rating_2':product_rating_2, 'product_review_cnt_2':product_review_cnt_2,\
            'insight_negative_list_2':insight_negative_list_2, 'insight_positive_list_2':insight_positive_list_2,\
            'product_price_2':product_price_2, 'product_image_url_2':product_image_url_2, 'product_stars_url_2':product_stars_url_2,\
            }

    # Get Product Info 3
    if len(asin_list) > 2:
        update_date_3 = product_name_3 =  product_image_url_3 = product_rating_3 = product_review_cnt_3 = product_price_3 = ''
        product_info_3 = AmazonProduct.objects.raw("SELECT id, update_date, product_name, product_rating, product_review_cnt, product_price, product_image_url \
            FROM ai_amazonproduct WHERE asin= %s ORDER BY update_date DESC LIMIT 1", [product_asin_3])
        if len(product_info_3) > 0 :
            for p in product_info_3:
                update_date_3 = p.update_date
                product_name_3 = p.product_name
                product_image_url_3 = p.product_image_url
                product_rating_3 = p.product_rating
                product_review_cnt_3 = p.product_review_cnt
                product_price_3 = p.product_price
        # if no date, scrape from Amazon
        else : 
            product_name_3, product_image_url_3, product_rating_3, product_review_cnt_3, product_price_3, update_date_3 = \
                scrape_product_info(product_asin_3)
        product_stars_url_3 = "review_" + str(int(float(product_rating_3)))+".png"
        insight_positive_list_3 = get_insights(str(product_asin_3), 'P')
        insight_negative_list_3 = get_insights(str(product_asin_3), 'N')

        context = {'update_date': update_date,'query_text': query_text, 'asin':asin_list[0],\
            'product_name':product_name, 'product_rating':product_rating, 'product_review_cnt':product_review_cnt,\
            'insight_negative_list':insight_negative_list, 'insight_positive_list':insight_positive_list,\
            'product_price':product_price, 'product_image_url':product_image_url, 'product_stars_url':product_stars_url,\

            'update_date_2': update_date_2, 'asin_2':product_asin_2,\
            'product_name_2':product_name_2, 'product_rating_2':product_rating_2, 'product_review_cnt_2':product_review_cnt_2,\
            'insight_negative_list_2':insight_negative_list_2, 'insight_positive_list_2':insight_positive_list_2,\
            'product_price_2':product_price_2, 'product_image_url_2':product_image_url_2, 'product_stars_url_2':product_stars_url_2,\

            'update_date_3': update_date_3, 'asin_3':product_asin_3,\
            'product_name_3':product_name_3, 'product_rating_3':product_rating_3, 'product_review_cnt_3':product_review_cnt_3,\
            'insight_negative_list_3':insight_negative_list_3, 'insight_positive_list_3':insight_positive_list_3,\
            'product_price_3':product_price_3, 'product_image_url_3':product_image_url_3, 'product_stars_url_3':product_stars_url_3,\
            }

    print("from result - context : "+ str(context))

    return render(request, 'ai/result.html', context)

def update(request):
    query_text = request.POST.get('query_text')

    print ("Now updating : " + query_text)

    asin_list = get_asin(query_text)

    if len(asin_list) > 0:
        update_insights(str(asin_list[0]))
    if len(asin_list) > 1:
        update_insights(str(asin_list[1]))
    if len(asin_list) > 2:
        update_insights(str(asin_list[2]))

    response = "Updated insights for the query : " + query_text

    return HttpResponse(response)

def update_insights(product_asin):
    model_input = []
    for x in range(10):
        new_model_input = review_scrape(product_asin, x, 'recent') + review_scrape(product_asin, x, 'helpful')
        print(product_asin)
        print("length of reviews : "+ str(len(new_model_input)))
        if len(new_model_input) < 10:
            break
        else:
            model_input = model_input + new_model_input
    print(">>>>>> MODEL INPUT : " + str(model_input))

    out_json_s_pos, out_json_s_neg = insights.main(["-j", model_input])
    out_json_s_pos_dict = ast.literal_eval(out_json_s_pos)
    out_json_s_neg_dict = ast.literal_eval(out_json_s_neg)
    print ("++++ Positive : " + out_json_s_pos)
    print ("---- Negative : " + out_json_s_neg)

    today_dt = datetime.datetime.now().strftime('%Y%m%d')
    update_dt = "0000"

    insight = Insight.objects.raw("SELECT id, update_date FROM ai_insight WHERE asin= %s ORDER BY update_date DESC LIMIT 1", [product_asin])
    if len(insight) > 0 :
        for p in insight:
            update_dt = p.update_date
    print("update_dt : " + update_dt + " / " + product_asin)

    cnt = 0
    response = ""
    if today_dt != update_dt:
        if len(out_json_s_pos_dict) > 0:
            for x in out_json_s_pos_dict:
                x_list = out_json_s_pos_dict.get(x)
                cnt = 0
                for y in x_list:
                    insight = Insight(asin=product_asin, update_date=today_dt, insight_seq=cnt, insight_type='P',\
                        insight_phrase=x, insight_text=y)
                    insight.save()
                    cnt = cnt + 1
            cnt = 0
        if len(out_json_s_neg_dict) > 0:
            for x in out_json_s_neg_dict:
                x_list = out_json_s_neg_dict.get(x)
                cnt = 0
                for y in x_list:
                    insight = Insight(asin=product_asin, update_date=today_dt, insight_seq=cnt, insight_type='N',\
                        insight_phrase=x, insight_text=y)
                    insight.save()
                    cnt = cnt + 1
        response = "Updated for the product" + product_asin
    else:
        response = "Have been already updated today for the product : " + product_asin + "  / today : " + today_dt

    return HttpResponse(response)


def get_insights(asin, insight_type):
    print("asin from get_insights : "+ asin)

    update_dt = ""
    insight = Insight.objects.raw("SELECT id, update_date FROM ai_insight WHERE asin= %s ORDER BY update_date DESC LIMIT 1", [asin])
    if len(insight) > 0 :
        for p in insight:
            update_dt = p.update_date

    insights = Insight.objects.raw("SELECT id, insight_phrase, insight_text FROM ai_insight WHERE asin= %s AND insight_type = %s AND update_date = %s ORDER BY update_date DESC ", [asin, insight_type, update_dt])
    insight_list = []
    cnt = 0
    temp_phrase = ""
    temp_text = ""
    for i in insights:
        if(temp_text == ""):
            temp_text = "&#8208;&nbsp" + i.insight_text.replace('<',' ').replace('>',' ')
        else:
            temp_text = temp_text + " <br><br> " + "&#8208;&nbsp" + i.insight_text.replace('<',' ').replace('>',' ')

        if (temp_phrase != i.insight_phrase):
            insight_list.append(['insight_'+insight_type+str(cnt), i.insight_phrase, temp_text])
            temp_text = ""
            cnt = cnt + 1
        temp_phrase = i.insight_phrase
        
    
    print(" ###  insight_type : " + insight_type)
    print(" ###  insight_list : " + str(insight_list))
    return insight_list


def test_insights():
    test_review = [{"reviewText":"A true cast iron pan is super smooth.", "overall":5.0},
        {"reviewText":"Enter the Lodge 12 inch cast iron skillet.", "overall":4.0},
        {"reviewText":"Just wash with hot water, without soap.", "overall":3.0},
        {"reviewText":"This is an absolutely amazing skillet!!  I use it ALL the time!!  I re-season it a bit as well to keep it going strong!", "overall":4.0},
        {"reviewText":"I wish I'd gotten a good cast iron skillet years ago, but I do enjoy making up for lost time!", "overall":4.0},
        {"reviewText":"My mother and mother-in-law both cook with skillets that have been well seasoned, and I'm very happy to achieve the same with mine.I love using my Cast Iron skillets just love them.", "overall":4.0},
        {"reviewText":"I like all my cast iron. This one though the tissue I wiped it with was black and wouldn't stop. It peeled a bit on the handle. I didn't get it. Out of all of my iron ware this one was so disgusting I washed it with soap. It's good now.", "overall":4.0},
        {"reviewText":"Just say no to chemical treatments on non stick pans, get yourself and your friends a few sizes of cast iron and have pans that you can pass down to your children, without all those unknown chemicals that are such a part of pans for the last few decades.", "overall":4.0},
        {"reviewText":"I've always bought the regular Lodge skillets and loved them.  Went with the pre-seasoned this time because I wanted this size.Wow, what a pain. badly pre-seasoned!). The coating flaked off, got my hands black, and smelled really rusty. This was horrible.I'm used to cast iron, for sure.", "overall":1.0},
        {"reviewText":"Only hot water and maybe salt if you need an abrasive.", "overall":2.0},
        {"reviewText":"I'm not a cook and didn't know what cast iron cooked like.", "overall":2.0},
        {"reviewText":"This was horrible.I'm used to cast iron, for sure.", "overall":1.0},
        {"reviewText":"Immediately, I noticed this pan seemed thinner and cheaper made. I noticed the bottom center seemed to be deteriorating. After 5 uses, I noticed what seems to be a crack forming. Now it will be thrown away. Very disappointed!", "overall":2.0},
        {"reviewText":"Oil first, heat it, then food in. I'm very disappointed. This is a great skillet, especially for the price.", "overall":1.0}]

    out_json_s_pos, out_json_s_neg = insights.main(["-j", test_review])

    print ("++++ Positive : " + out_json_s_pos)
    print ("---- Negative : " + out_json_s_neg)

def asin_scrape(query_text):
    print("query_text : " + str(query_text))
    url_pre = 'https://www.amazon.com/s?k='
    url_post = '&ref=nb_sb_noss_2'

    parse_text_start = '<div class="a-row a-badge-region"><span id="'
    parse_text_end = '" class="a-badge"'

    url = url_pre + query_text + url_post
    print(url)

    time.sleep(0.7*random.random())
    response = requests.get(url, headers=headers, proxies=proxies).text
    parsed_asin_list = parse_page(response, parse_text_start, parse_text_end, 'list')

    return parsed_asin_list

def get_asin(query_text):
    print("query_text : " + str(query_text))
    url_pre = 'https://www.amazon.com/s?k='
    url_post = '&ref=nb_sb_noss_2'

    trim_pre = '<span data-component-type="s-search-results"'
    parse_text_start = '<div data-asin="'
    parse_text_end = '" data-index="'

    ad_parse_text_start = '&quot;name&quot;:&quot;sp-info-popover-'
    ad_parse_text_end = '&quot;'

    url = url_pre + query_text + url_post
    print(url)
    time.sleep(0.5*random.random())
    response = requests.get(url, headers=headers, proxies=proxies).text
    trim_response = trim_string_pre(response, trim_pre)

    parsed_asin_list = parse_page(trim_response, parse_text_start, parse_text_end, 'list')
    parsed_ad_asin_list = parse_page(response, ad_parse_text_start, ad_parse_text_end, 'list')
    print("parsed_ad_asin_list : " + str(parsed_ad_asin_list))

    for x in parsed_ad_asin_list:
        if x in parsed_asin_list:
            parsed_asin_list.remove(x)
        if (len(x) > 10 and x in parsed_asin_list):
            parsed_asin_list.remove(x)


    return parsed_asin_list

def review_scrape(product_asin, page_number, filter_by):
    url_pre = 'https://www.amazon.com/product-reviews/'
    url_post = '/reviewerType=all_reviews&sortBy=recent&pageNumber=0/ref=cm_cr_getr_d_paging_btm_next_'
    url_post_2 = '?pageNumber='
    url_post_3 = '&sortBy='

    parse_text_start = 'class="a-section celwidget">'
    parse_text_end = 'Report abuse'

    url = url_pre + product_asin + url_post + str(page_number) + url_post_2 + str(page_number) + url_post_3 + filter_by
    print(url)
    print("Scraping... "+product_asin + " / Page : " + str(page_number))
    time.sleep(0.5*random.random())
    response = requests.get(url, headers=headers, proxies=proxies).text

    if (response.find(parse_text_start) > 0):
        print ("Scraping SUCCESS!")
    else:
        print ("Scraping FAIL!" + response[:100])
        return []

    parsed_review = parse_page(response, parse_text_start, parse_text_end, 'list')
    print ("Length of Review : " + str(len(parsed_review)))

    model_input = []

    asin = product_asin
    for x in range(len(parsed_review)):
        print("Review : " + str(x))
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

        review_rating = parse_string(parse_block, '<span class="a-icon-alt">', ' out of 5 stars</span></i>')
        parse_block = trim_string(parse_block, '<span class="a-icon-alt">', ' out of 5 stars</span></i>')
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

        model_input = model_input + [{"reviewText":review_text, "overall":float(review_rating)}]

        amazonReview = AmazonReview(reviewer_id=reviewer_id, reviewer_name=reviewer_name,\
            asin=asin, review_rating=review_rating, review_title=review_title,\
            review_date=review_date, review_text=review_text, review_helpful=review_helpful)
        amazonReview.save()

    return model_input

def scrape_product_info(product_asin):
    url_pre = 'https://www.amazon.com/dp/'

    url = url_pre + product_asin
    print(url)
    time.sleep(0.5*random.random())
    response = requests.get(url, headers=headers, proxies=proxies).text

    product_name2  = parse_string(response, '<span class="a-list-item"><div class="a-section"><img alt="', '" src="')
    print (" product_name ###### : " + product_name2)

    product_name  = parse_string(response, '<span id="productTitle" class="a-size-large">', '</span>')
    print (" product_name2 ###### : " + product_name)

    product_image_url  = parse_string(response, 'data-old-hires="', '"  class="')
    print (" product_image_url ###### : " + product_image_url)

    product_rating  = parse_string(response, 'averageStarRating"><span class="a-icon-alt">', ' out of 5 stars</span>')
    print (" product_rating ###### : " + product_rating)

    product_price  = parse_string(response, 'priceBlockBuyingPriceString">', '</span>')
    print (" product_price ###### : " + product_price)

    product_review_cnt  = parse_string(response, '<span id="acrCustomerReviewText" class="a-size-base">', ' customer reviews</span>')
    product_review_cnt = product_review_cnt.replace(",", "")
    print (" product_review_cnt ###### : " + product_review_cnt)

    update_date = datetime.datetime.now().strftime('%Y%m%d')

    amazonProduct = AmazonProduct(product_name=product_name, product_image_url=product_image_url,\
        asin=product_asin, product_rating=product_rating, product_review_cnt=product_review_cnt, \
        product_price = product_price, update_date=update_date)
    amazonProduct.save()

    return product_name, product_image_url, product_rating, product_review_cnt, product_price, update_date

    

def parse_page(original_text, parse_text_start, parse_text_end, string_list):
    print("Now in parse_page!")
    parsed_list = []
    parsed_string = ""
    original_text_processing = ""
    if(original_text.find(parse_text_start) > 0):
        print("[parse_page] Found : " + parse_text_start)
        original_text_processing = original_text[original_text.find(parse_text_start)+len(parse_text_start):]

        cnt=0
        while cnt < 10:
            parsed_text = original_text_processing[:original_text_processing.find(parse_text_end)]
            print("[parse_page] parsed_text length : " + str(len(parsed_text)))

            if (len(parsed_text) > 0 and len(parsed_text) < 10000):
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
        print("[parse_page] Not Found : " + parse_text_start)
        parsed_list = ['NO_SEARCH_RESULT']
        parsed_string = 'NO_SEARCH_RESULT'

    print("Result! : " + str(len(parsed_list)))

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

def trim_string_pre(original_text, parse_text_start):
    original_text_processing = original_text
    if(original_text.find(parse_text_start) > 0):
        original_text_processing = original_text[original_text.find(parse_text_start)+len(parse_text_start):]
    return original_text_processing
