# Scrapy settings for py203scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
# http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'py203scraper'

SPIDER_MODULES = ['py203scraper.spiders']

#clutter
#NEWSPIDER_MODULE = 'py203scraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'py203scraper (+http://www.yourdomain.com)'

#disabling problematic extions.
#We don't need the feed exporter, we use pipelines for data output
#this is probably the only setting, so far, that should stay in this file
# the others need to be moved to scrapyd in some way
#TODO: remove further unnecessary extensions
EXTENSIONS = {
    'scrapy.contrib.feedexport.FeedExporter': None
}

SCRAPER_DB = {'user': 'myTasteScraper',
              'passwd': 'BWh2pLCyDZb5s6r4',
              'db': '203scraper',
              'host': 'scraper-db.p203.se',
              'charset': "utf8",
              'use_unicode': True}

REDIS_HOST = 'scraper-db.p203.se'
REDIS_PORT = 6379
REDIS_DATABASE = 0
REDIS_ITEM_QUEUE_SIZE = 10

SERVER_ID = None

MAX_RECIPES_BY_BLOG = 10000000

try:
    from local_settings import *
except:
    pass