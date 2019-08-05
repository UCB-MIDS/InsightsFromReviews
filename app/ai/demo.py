from insights import insights

# File with the reviews database
file = '/Users/gkhanna/Downloads/reviews_Home_and_Kitchen_5.json'
pl = 'B00006JSUA'

print('Getting reviews for ' + pl + ' out of ' + file)

# insights.main(["-j", test_review])

insights.main(["-i", file, "-a", pl])
