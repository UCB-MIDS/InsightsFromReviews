Python command line and API for getting insights out of reviews

Usage

python insights.py -i dbfile -j jsonString -a asin

where dbfile is the full path to the JSON reviewsDB (Default used for development)
jsonString is the serialized JSON (From Scraped data)
asin is the Amazon ID in case we want to filter the default DB by asin

The functions returns serialized JSON (a positive and a negative phrases string). It also writes the same in 2 files
pos_features.json
neg_featues.json

Example usage:

python insights.py -h
insights.py -i <dbfile> -j <jsonString> -a <asin>

python insights.py -c 500
This loads only first 500 reviews from the default DB

python insights.py -a 'B00006JSUA'
Loads all reviews matching the ASIN from the default DB

python insights.py -j "LONG STRING"
Loads all reviews from the JSON string
