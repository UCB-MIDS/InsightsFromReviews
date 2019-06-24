from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from fake_useragent import UserAgent

import random
import requests



# Create your views here.
def index(request):
    #request.session['query_text'] = 'wassup'
    return render(request, 'ai/index.html')

def result(request):
    query_text = request.POST.get('query_text')
    asin_list = asin_scrape(query_text)

    review_list = []
    for x in range(5):
        review_list = review_list + review_scrape(asin_list[0],x)

    response = "Search results for the query : " + query_text + " <br> >> Product ASINs : " + str(asin_list)\
     + "<br> >> Reviews = <br><br>" + str(review_list)
    return HttpResponse(response)


def asin_scrape(query_text):
    url_pre = 'https://www.amazon.com/s?k='
    url_post = '&ref=nb_sb_noss_2'

    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'}
    proxies_list = ["35.198.69.233:80","178.128.11.215:80","54.226.53.87:80"]
    proxies = {'http': random.choice(proxies_list)}

    parse_text_start = '=UTF8&amp;asin='
    parse_text_end = '&amp;ref'

    url = url_pre + query_text + url_post
    print(url)

    response = requests.get(url, headers=headers, proxies=proxies).text
    print(response[:300])
    print(">>>> " + str(response.find(parse_text_start)))

    parsed_asin_list = []
    if(response.find(parse_text_start) > 0):
        response_processing = response[response.find(parse_text_start)+len(parse_text_start):]

        cnt=0
        while cnt < 10:
            parsed_asin = response_processing[:response_processing.find(parse_text_end)]
            parsed_asin_list.append(parsed_asin)
            cnt += 1

            if(response.find(parse_text_start) > 0):
                response_processing = response_processing[response_processing.find(parse_text_start)+len(parse_text_start):]
            else:
                break
    else:
        parsed_asin_list = ['NO_SEARCH_RESULT']

    return parsed_asin_list


def review_scrape(product_asin, page_number):
    url_pre = 'https://www.amazon.com/product-reviews/'
    url_post = '/reviewerType=all_reviews&sortBy=recent&pageNumber='

    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'}
    proxies_list = ["35.198.69.233:80","178.128.11.215:80","54.226.53.87:80"]
    proxies = {'http': random.choice(proxies_list)}

    parse_text_start = 'review-text-content"><span class="">'
    parse_text_end = '</span>'

    url = url_pre + product_asin + url_post + str(page_number)
    print(url)
    response = requests.get(url, headers=headers, proxies=proxies).text

    parsed_review_list = []
    if(response.find(parse_text_start) > 0):
        response_processing = response[response.find(parse_text_start)+len(parse_text_start):]

        cnt=0
        while cnt < 10:
            parsed_review = response_processing[:response_processing.find(parse_text_end)]
            parsed_review_list.append(parsed_review)
            cnt += 1

            if(response.find(parse_text_start) > 0):
                response_processing = response_processing[response_processing.find(parse_text_start)+len(parse_text_start):]
            else:
                break
    else:
        parsed_review_list = ['NO_SEARCH_RESULT']

    return parsed_review_list



