import json
import code

json_data = open('items.json')
data = json.load(json_data)

trade_mentions = 0
comment_count = 0
listing_trade_mentions = 0

for listing in data:
    comments = listing["comments"]
    comment_count = len(comments) + comment_count

    found = False
    for comment_dict in comments:
        username, comment, date = comment_dict.values()


        if "trade" in comment:
            trade_mentions = trade_mentions + 1

            if not found:
                found = True
                listing_trade_mentions = listing_trade_mentions + 1


print "Number of listings: " + str(len(data))
print "Listing that mention trade: " + str(listing_trade_mentions)
print "Number of trade mentions: " + str(trade_mentions)
print "Number of comments: " + str(comment_count)
print "Percentage of comments: " + str((float(trade_mentions)/comment_count) * 100)
print "Percentage of listings: " + str((float(listing_trade_mentions)/len(data)) * 100)
#code.interact(local=locals())

json_data.close()
