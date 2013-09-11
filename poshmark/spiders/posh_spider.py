from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from poshmark.items import PoshmarkPost

class PoshSpider(CrawlSpider):
    # Here goes the crawler name
    name = 'poshmark'
    # Domains for which the crawler is constrained too
    allowed_domains = ['poshmark.com']
    # URLs where the crawler should start scraping
    start_urls = ['http://poshmark.com/category/Accessories',
                  'http://poshmark.com/category/Boots',
                  'http://poshmark.com/category/Clutches_&_Wallets',
                  'http://poshmark.com/category/Denim',
                  'http://poshmark.com/category/Dresses_&_Skirts',
                  'http://poshmark.com/category/Handbags',
                  'http://poshmark.com/category/Jackets_&_Blazers',
                  'http://poshmark.com/category/Jewelry',
                  'http://poshmark.com/category/Outerwear',
                  'http://poshmark.com/category/Pants',
                  'http://poshmark.com/category/Shoes',
                  'http://poshmark.com/category/Sweaters',
                  'http://poshmark.com/category/Tops',
                  'http://poshmark.com/category/Other']

    # Rules on what the scraper should do with the links it finds
    rules = (
        # Process listings
        Rule(SgmlLinkExtractor(allow='listing/[a-z0-9]+',
                               deny='like'),
                               callback='parse_listing'),
      )

    def parse_listing(self, response):
        """
        This function parses a single Poshmark listing. Some contracts
        are mingled with this docstring.

        @url http://poshmark.com/listing/51cb4195bdf51c5c9d02cd28
        @returns items 1 1
        @returns requests 0 0
        @scrapes brand comments description price size title
        """

        hxs = HtmlXPathSelector(response)
        hxs_comments = hxs.select("//div[@class='listing-comments-con']/div[@class='item comment']")

        get = lambda obj, str: safe_list_get(obj.select(str).extract(), 0)

        comments = []

        for comment in hxs_comments:
            pcomment = {}
            pcomment['username'] = get(comment, ".//a[@class='grey commentor']/text()")
            pcomment['comment'] = get(comment, "text()")
            pcomment['date'] = get(comment, ".//small/text()")
            comments.append(pcomment)

        pp = PoshmarkPost()
        details = hxs.select("//div[@class='item-details-widget']")
        pp['title'] = get(details, ".//h4/text()")
        pp['description'] = get(hxs, "//div[@class='description']/text()")
        pp['size'] = get(details, ".//li[@class='size']/a/text()")
        pp['brand'] = get(details, ".//li[@class='brand']/a/text()")
        pp['price'] = get(details, ".//span[@class='actual']/text()")
        pp['comments'] = comments

        yield pp

    def parse_start_url(self, response):
        for url in self.start_urls:
            for i in range(1, 10):
                page = '?max_id=' + str(i) + '&page=' + str(i)
                yield Request(url + page, self.parse)

    # Let's initialize the classes we are inheriting from.
    def __init__(self):
        CrawlSpider.__init__(self)

def safe_list_get(l, idx, default=''):
    try:
        return l[idx]
    except IndexError:
        return default
