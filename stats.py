#!/usr/bin/python
#import code

import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from fuzzywuzzy import fuzz

def chart(occurance_list):
    hour_list = [t.month for t in occurance_list]
    numbers=[x for x in xrange(1,13)]
    labels=map(lambda x: str(x), numbers)
    plt.xticks(numbers, labels)
    plt.xlim(0,24)
    plt.hist(hour_list)
    plt.show()

json_data = open('items.json')
data = json.load(json_data)

trade_mentions = 0
comment_count = 0
listing_trade_mentions = 0
dates = []
prices = []
brands = []
for listing in data:
    comments = listing["comments"]
    comment_count = len(comments) + comment_count
    p = int(listing["price"][1:])
    if p < 500:
        prices.append(p)

    curr_brand = listing["brand"]
    #print listing["brand"]

    exists = False
    for brand in brands:
        for brand2 in brands:
            if brand != brand2:
                if fuzz.partial_ratio(brand, brand2) > 80:
                    exists = True
                    break

    if not exists:
        brands.append(curr_brand)

    found = False
    for comment_dict in comments:
        username, comment, date = comment_dict.values()
        time_string = "%b %d %I:%M%p"
        get_time_obj = lambda x: datetime.strptime(x, time_string)

        if "trade" in comment:
            trade_mentions = trade_mentions + 1

            if not found:
                found = True
                try:
                    dates.append(get_time_obj(date))
                except:
                    pass
                listing_trade_mentions = listing_trade_mentions + 1

print "Number of listings: " + str(len(data))
print "Listing that mention trade: " + str(listing_trade_mentions)
print "Number of trade mentions: " + str(trade_mentions)
print "Number of comments: " + str(comment_count)
print "Percentage of comments: " + str((float(trade_mentions)/comment_count) * 100)
print "Percentage of listings: " + str((float(listing_trade_mentions)/len(data)) * 100)
print "Mean price: " + str(np.mean(np.array(prices)))
print brands
print len(brands)
# chart(dates)

json_data.close()
