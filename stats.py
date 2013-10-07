#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymongo
import numpy as np
import matplotlib.pyplot as plt
import simplekml
import sys
import time
from datetime import datetime
from pygeocoder import Geocoder, GeocoderError

#Clean prices
def clean_prices(poshmark):
    for p in poshmark.find({"price": {"$exists": True}}):
        price =  int(p["price"][1:])
        p["price"] = price
        poshmark.save(p)

#Clean profile numbers
def clean_profiles(poshmark):
    for p in poshmark.find({"user_name": {"$exists": True}}):
        get_num = lambda num: int(num.replace(',', ''))
        listings = get_num(p["listings"])
        followers = get_num(p["followers"])
        following = get_num(p["following"])
        p["listings"] = listings
        p["followers"] = followers
        p["following"] = following
        poshmark.save(p)

def print_percentage(title, count, tot):
    print title + str(percentage(count, tot))

def percentage(count, tot):
    return (float(count)/tot) * 100

def chart_brands(brands, values):
    fig, ax = plt.subplots()
    ax.set_xticklabels(brands, rotation=-90)
    x_pos = np.arange(len(brands))
    plt.bar(x_pos, values, align='center')
    plt.xticks(x_pos, brands)
    plt.xlabel('Brands')
    plt.ylabel('No. Listings')
    plt.title('Top brands')

    plt.show()

def chart_dates(occurance_list):
    month_list = [t.month for t in occurance_list]
    numbers=[x for x in xrange(1,13)]
    labels=map(lambda x: str(x), numbers)
    plt.xticks(numbers, labels)
    plt.xlim(0,24)
    plt.hist(month_list)
    plt.show()

def chart_prices(prices):
    chart(prices, 'Prices', 'Listings', 'Prices Histogram')

def chart(vals, xlabel="", ylabel="", title = "", buckets=10):
    fig, ax = plt.subplots()
    counts, bins, patches = plt.hist(vals, buckets)

    # Set the ticks to be at the edges of the bins.
    ax.set_xticks(bins)

    # Label the raw counts and the percentages below the x-axis...
    bin_centers = 0.5 * np.diff(bins) + bins[:-1]
    for count, x in zip(counts, bin_centers):
        # Label the raw counts
        ax.annotate(str(count), xy=(x, 0), xycoords=('data', 'axes fraction'),
                    xytext=(0, -18), textcoords='offset points', va='top', ha='center')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    # Give ourselves some more room at the bottom of the plot
    plt.subplots_adjust(bottom=0.15)
    plt.show()

def create_map(profiles):
    options = ("no", "don't", "not", u"❌", "sorry", u"🚫", u"✋", "paypal", "pp",
        "negociable", "negotiable", "negoatiating", "negotiate",
        "offer", "deal", "lower")
    kml = simplekml.Kml()
    coords_map = {}
    g = Geocoder()
    for p in profiles:
        location = p["location"]

        # Check if it's just a message and not a location
        if any(o in location for o in options):
            continue

        # We can't hit the API too hard
        time.sleep(6)
        try:
            coords = coords_map[location]
        except KeyError:
            try:
                results = g.geocode(location)
                lat, lng = results.coordinates
                coords = [(lng, lat)]
                coords_map[location] = coords
                pnt = kml.newpoint()
                pnt.style.labelstyle.scale = 2  # Make the text twice as big
                pnt.name =  p["user_name"]
                pnt.coords = coords

                # Save the KML
                kml.save("poshmark.kml")
            except GeocoderError as e:
                print e

def process_comments(comments):
    found = False
    trade_mentions = 0
    dates = []
    get_time_obj = lambda x: datetime.strptime(x, time_string)
    for comment_list in comments:
        username, comment, date = comment_list.values()
        time_string = "%b %d %I:%M%p"

        if "trade" in comment:
            trade_mentions += 1

            if not found:
                found = True
                try:
                    dates.append(get_time_obj(date))
                except:
                    pass

    return trade_mentions, dates

# Access poshmark collection from our db
client = pymongo.MongoClient("localhost", 27017)
db = client.scrapy
poshmark = db.items

# Lists
atlantians = []
georgians = []
prices = []
listings_count = []
followers_count = []
following_count = []

# Dictionaries
brands = {}
sold_brands = {}


# Counts
listing_trade_mentions = 0
total_trade_mentions = 0
total_comments = 0
trade_listings = 0
no_trade_listings = 0
bundle_listings = 0
paypal_listings = 0
negotiable_listings = 0

# Listings that cost over $200 are usually not real
listings = poshmark.find({"price": {"$lt": 200}})
tot_listings = poshmark.find({"price": {"$exists": True}})
profiles = poshmark.find(
    {"user_name": {"$exists": True},
     "followers": {"$lt": 1000},
     "following": {"$lt": 1000},
     "listings": {"$lt": 1000}})

create_map(profiles)
sys.exit(0)

for p in listings:
    prices.append(p["price"])
    brand = p["brand"].lower()
    sold = p["sold"].lower()

    # Check that brand data is available
    if brand:
        if not brand in brands:
            brands[brand] = 1
        else:
            brands[brand] += 1

        if sold == "yes":
            if not brand in sold_brands:
                sold_brands[brand] = 1
            else:
                sold_brands[brand] += 1

    comments = p["comments"]
    if comments:
        total_comments = total_comments + len(comments)
        trade_mentions, dates  = process_comments(comments)
        total_trade_mentions = trade_mentions + total_trade_mentions
        if trade_mentions > 0:
            listing_trade_mentions += 1

for p in profiles:
    listings_count.append(p["listings"])
    followers_count.append(p["followers"])
    following_count.append(p["following"])
    location = p["location"].lower()

    if "atlanta" in location:
        atlantians.append(p)
        georgians.append(p)

    else:
        options = ("georgia", "ga")
        if any(o in location for o in options):
            georgians.append(p)

    if "trade" in location:
        trade_listings += 1

        options = ("no", "don't", "not", u"❌", "sorry", u"🚫", u"✋")
        if any(o in location for o in options):
            no_trade_listings += 1
        if "bundle" in location:
            bundle_listings += 1

        options = ("paypal", "pp")
        if any(o in location for o in options):
            paypal_listings += 1

        options = ("negociable", "negotiable", "negoatiating",
        "negotiate", "offer", "deal", "lower")
        if any(o in location for o in options):
            negotiable_listings += 1

get_mean = lambda val: str(np.mean(np.array(val)))
get_median = lambda val: str(np.median(np.array(val)))

print "* Stats"

print "** General Stats"
print "- Ok?: " + str(poshmark.count() == \
                      (tot_listings.count() + profiles.count()))
print "- Total number of documents in collection: " + str(poshmark.count())
print "- Total number of listings: " + str(tot_listings.count())
print "- Listings < $200, i.e. real listings: " + str(listings.count())
print "- Total number of of profiles: " + str(profiles.count())
print "- Total number of comments: " + str(total_comments)
print "- Average price: " + get_mean(prices)
print "- Mean price: " + get_median(prices)

print "** On Trade"
print "- Listings that mention the word trade: " + str(listing_trade_mentions)
print_percentage("- % of listings that mention trade: ", \
                 listing_trade_mentions, listings.count())
print "- Number of trade mentions in comments: " + str(total_trade_mentions)
print_percentage("- % of comments that mention trade: ", \
                 total_trade_mentions, total_comments)

print "** Profile Stats"
print "- Average number of listings: " + get_mean(listings_count)
print "- Mean number of listings: " + get_median(listings_count)
print "- Average number of followers: " + get_mean(followers_count)
print "- Mean number of followers: " + get_median(followers_count)
print "- Average number of following: " + get_mean(following_count)
print "- Mean number of following: " + get_median(following_count)
print_percentage("- % That mention trade on profile: ", \
                 trade_listings, profiles.count())
print_percentage("- % That say NO trade on profile: ", \
                 no_trade_listings, profiles.count())
print_percentage("- % That mention bundles: ", \
                 bundle_listings, profiles.count())
print_percentage("- % That mention Paypal: ", paypal_listings, profiles.count())
print_percentage("- % That mention that the price is negotiable: ", \
                 negotiable_listings, profiles.count())

print "** Locals"
print "- Atlantians: " + str(len(atlantians))
print "- Georgians: " + str(len(georgians))

chart_prices(prices)
chart(listings_count, title="Listings", buckets=15)
chart(followers_count, title="Followers")
chart(following_count, title="Following", buckets=15)

sorted_brands = sorted(brands.iteritems(), key = lambda (k, v): (v, k))
top_brands = sorted_brands[-15:]
chart_brands([k for k, v in top_brands], [v for k, v in top_brands])

sorted_brands = sorted(sold_brands.iteritems(), key = lambda (k, v): (v, k))
top_brands = sorted_brands[-15:]
chart_brands([k for k, v in top_brands], [v for k, v in top_brands])
# chart(dates)
