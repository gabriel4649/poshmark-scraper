# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class PoshmarkPost(Item):
    title = Field()
    description = Field()
    brand = Field()
    size = Field()
    price = Field()
    comments = Field()
