# import json
from insights import insights
# import codecs
import ast

# File with the reviews database
file = '/Users/gkhanna/Downloads/reviews_Home_and_Kitchen_5.json'
# file = 'B00006JSUA.txt'
pl = 'B00006JSUA'

print('Getting reviews for ' + pl + ' out of ' + file)

# How its called from the application
# insights.main(["-j", test_review])

# For demo taking reviews for a single asin from the db
insights.main(["-i", file, "-a", pl])
# insights.main(["-i", file])
