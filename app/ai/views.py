from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

import requests



# Create your views here.
def index(request):
    #request.session['query_text'] = 'wassup'
    return render(request, 'ai/index.html')

def result(request):
    query_text = request.POST.get('query_text')
    response = "Search results for the query : " + query_text + " >> asin= : " + str(keyword_search(query_text))
    return HttpResponse(response)


def keyword_search(query_text):
    url_pre = 'https://www.amazon.com/s?k='
    url_pro = '&ref=nb_sb_noss_2'

    parse_text_start = '=UTF8&amp;asin='
    parse_text_end = '&amp;ref'

    url = url_pre + query_text + url_pro

    response = requests.post(url).text

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