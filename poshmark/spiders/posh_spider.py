from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from poshmark.items import PoshmarkPost, PoshmarkProfile
from datetime import datetime, timedelta

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
                  'http://poshmark.com/category/Other',
                  'http://poshmark.com/parties']

    # Rules on what the scraper should do with the links it finds
    rules = (
        # Process listings
        Rule(SgmlLinkExtractor(allow='listing/[a-z0-9]+',
                               deny='like'),
                               callback='parse_listing'),
        # Process user profiles
        Rule(SgmlLinkExtractor(allow='closet/[a-z0-9]+'),
             callback='parse_profile'),
        # Follow parties for listing links
        Rule(SgmlLinkExtractor(allow='party/[a-z0-9]+')),
        # Let's see more parties
        # http://poshmark.com/parties?last_event_id=522e58197aea0b062208ddba&last_event_time=2013-09-10T16%3A00%3A00Z
        Rule(SgmlLinkExtractor(allow='parties\?.*')),
        # Let's see more of that party
        # http://poshmark.com/party/5234f11682fe0659d402d8f0?max_id=1379278800.335
        Rule(SgmlLinkExtractor(allow='party/[a-z0-9]+\?max_id=.*')),
        # I want MOAR listings
        #http://poshmark.com/category/Accessories?max_id=2
        Rule(SgmlLinkExtractor(allow='category/.*')),
      )

    def parse_listing(self, response):
        """
        This function parses a single Poshmark listing. Some contracts
        are mingled with this doc string.

        @url http://poshmark.com/listing/51cb4195bdf51c5c9d02cd28
        @returns items 1 1
        @returns requests 0 0
        @scrapes brand comments description price size title
        """

        hxs = HtmlXPathSelector(response)
        hxs_comments = hxs.select("//div[@class='listing-comments-con']/div[@class='item comment']")

        comments = []

        for comment in hxs_comments:
            pcomment = {}
            pcomment['username'] = get(comment, ".//a[@class='grey commentor']/text()")
            pcomment['comment'] = get(comment, "text()")
            raw_date = get(comment, ".//small/descendant-or-self::*/text()")
            #Jul 18 10:43AM
            time_string = "%b %d %I:%M%p"
            get_time_obj = lambda x: datetime.strptime(x, time_string)

            if 'ago' in raw_date:
                try:
                    n_ago = int(raw_date.split()[0])
                except:
                    if 'yesterday' in raw_date:
                        delta = timedelta(days=1)
                    if 'second' in raw_date:
                        delta = timedelta(seconds=1)
                    if 'hour' in raw_date:
                        delta = timedelta(hours=1)

                if 'seconds' in raw_date:
                    delta = timedelta(seconds=n_ago)
                elif 'minutes' in raw_date:
                    delta = timedelta(minutes=n_ago)
                elif 'hours' in raw_date:
                    delta = timedelta(hours=n_ago)
                elif 'days' in raw_date:
                    delta = timedelta(days=n_ago)

                date = datetime.now() - delta
                date = date.strftime(time_string)
            else:
                date = raw_date

            pcomment['date'] = date
            comments.append(pcomment)

        pp = PoshmarkPost()
        details = hxs.select("//div[@class='item-details-widget']")
        pp['title'] = get(details, ".//h4/text()")
        pp['description'] = get(hxs, "//div[@class='description']/text()")
        pp['date'] = get(details, ".//span[@class='context']/text()").split('Posted ')[1]
        pp['size'] = get(details, ".//li[@class='size']/a/text()")
        pp['brand'] = get(details, ".//li[@class='brand']/a/text()")
        pp['price'] = get(details, ".//span[@class='actual']/text()")

        if get(details, ".//span[@class='sprite sold-tag']"):
            sold = "Yes"
        else:
            sold = "No"

        pp['sold'] = sold
        pp['comments'] = comments
        pp['number_of_comments'] = len(comments)

        likers = hxs.select("//div[@class='listing-likes-con']/span/a/text()").extract()
        pp['likers'] = likers
        pp['likes'] = len(likers)
        pp['url'] = response.url

        return pp

    def parse_profile(self, response):
        hxs = HtmlXPathSelector(response)

        pp = PoshmarkProfile()
        pp['user_name'] = get(hxs, "//h4[@class='user-name']/text()")
        pp['listings'], pp['followers'], pp['following'] = hxs.select("//ul[@class='pipe2']/li/a/strong/text()").extract()
        pp['location'] = get(hxs, "//span[@class='city']/text()")
        pp['website'] = get(hxs, "//div[@class='web-site-con']/a/@href")
        pp['url'] = response.url

        return pp

    # def parse_start_url(self, response):
    #     for url in self.start_urls:
    #         if not 'parties' in url:
    #             for i in range(1, 120):
    #                 page = '?max_id=' + str(i) + '&page=' + str(i)
    #                 yield Request(url + page, self.parse)

    # Let's initialize the classes we are inheriting from.
    def __init__(self):
        CrawlSpider.__init__(self)

def safe_list_get(l, idx, default=''):
    try:
        return l[idx]
    except IndexError:
        return default

def get(obj, str):
    return safe_list_get(obj.select(str).extract(), 0)
