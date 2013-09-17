# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class PoshmarkPost(Item):
    title = Field()
    description = Field()
    date = Field()
    brand = Field()
    size = Field()
    price = Field()
    sold = Field()
    comments = Field()
    number_of_comments = Field()
    likers = Field()
    likes = Field()
    url = Field()

class PoshmarkProfile(Item):
    user_name = Field()
    listings = Field()
    followers = Field()
    following = Field()
    location = Field()
    website = Field()
