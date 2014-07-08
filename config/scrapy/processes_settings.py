import MySQLdb.cursors

BLOG_SCRAP_SITES = ['p203_recipes', 'tuasreceitas_com_br']
SITE_SCRAP_SITES = ['tuasreceitas_com_br']


# HITTARECEPT_SITES = ['alldishes_co_uk',
#'alleoppskrifter_no',
#'everyrecipe_com_au',
#'everyrecipe_co_nz',
#'everyrecipe_co_za',
#'findeopskrifter_dk',
#'lestevesreceptes_cat',
#'recipesus_com',
#'todareceta_co_ve',
#'tuasreceitas_com_br',
#'tudoreceita_pt',
#'volrecepten_nl',
#'znajdzprzepisy_pl']

#REDIS_INSTANCE = redis.Redis(host='dev.p203.se', port=6379, db=0)

MYSQL_MASTERDB_DETAILS = {'user': 'root',
                          'passwd': 'd4mpsql!',
                          'db': '203admin_scraper_test',
                          'host': 'dev.p203.se',
                          'charset': "utf8",
                          'cursorclass': MySQLdb.cursors.SSDictCursor,
                          'use_unicode': True}

#SCRAPYD_URL = 'http://dev.p203.se:6800/'
SCRAPYD_URL = 'http://dev.p203.es:7777/'


##queue_recipe_blog_scraping deamon settings
QRB_PIDFILE = '/home/vagrant/scraper-daemons/QRB.pid'
QRB_STDOUT = '/home/vagrant/scraper-daemons/logsdump'
QRB_STDERR = '/home/vagrant/scraper-daemons/logsdump'

QUEUE_RELIEF_INTERVAL = 8
SCRAPYD_MAX_QUEUE_SIZE = 2000


##update image hashes deamon settings
UIH_PIDFILE = '/home/vagrant/scraper-daemons/UIH.pid'
UIH_STDOUT = '/home/vagrant/scraper-daemonslogsdump'
UIH_STDERR = '/home/vagrant/scraper-daemons/logsdump'

IMAGE_REQUEST_TIMEOUT = 2
IMAGE_BATCH_SIZE = 30

ENVIRONMENT = "DEV"

try:
    from local_settings import *
except:
    pass

