#!/usr/bin/env python
 # -*- coding: utf-8 -*-

from vagrant import vagrant
from fabric.api import cd, sudo, run, put, settings, task
from fabric.operations import prompt
from fabric.contrib.files import exists
import getpass
import pkg_resources

"""
 ===========================
    Scrapy installation
 ===========================
"""
def scrapy_file(filepath):
    return pkg_resources.resource_filename(__name__,
                                           '/config/scrapy/{0}'.format(filepath))

def scrapyd_file(filepath):
    return pkg_resources.resource_filename(__name__,
                                           '/config/scrapyd/{0}'.format(filepath))

def graphite_file(filepath):
    return pkg_resources.resource_filename(__name__,
                                           '/config/graphite/{0}'.format(filepath))

def statsd_file(filepath):
    return pkg_resources.resource_filename(__name__,
                                           '/config/statsd/{0}'.format(filepath))

def grafana_file(filepath):
    return pkg_resources.resource_filename(__name__,
                                           '/config/grafana/{0}'.format(filepath))

def command_exists(command):
    """
    Checks if the command 'command' exists
    """
    result = False
    with settings(warn_only=True):
        checked = run('command -v %s' % command)
        if checked.return_code == 0:
            result = True

    return result

def move_scrapy_configs():
    put(scrapy_file('processes_settings.py'), '/vagrant/python-scraper/processes/settings.py')
    put(scrapy_file('scraper_settings.py'), '/vagrant/python-scraper/py203scraper/settings.py')
    put(scrapy_file('scrapy_settings.py'), '/vagrant/python-scraper/scrapy.cfg')

def move_scrapyd_configs(db_number):
    with cd('/vagrant/'):
        run('cp config/scrapyd/scrapyd.conf scrapyd-fancy-ui/scrapyd.conf')
        s = open('scrapyd-fancy-ui/scrapyd.conf').read()
        s = s.replace('{{REDIS_DB_NUMBER}}', str(db_number))
        f = open('scrapyd-fancy-ui/scrapyd.conf', 'w')
        f.write(s)
        f.close()

def _download_projects(username, password, db_number):
    with cd('/vagrant'):
        if not exists('/vagrant/python-scraper') or not exists('/vagrant/scrapyd-fancy-ui'):
            print "In order to download the scraper repository, we need your username and password to continue."
        if not exists('/vagrant/python-scraper'):
            run('git clone https://%s:%s@github.com/%s/python-scraper.git' % (username, password, username))
            move_scrapy_configs()
        if not exists('/vagrant/scrapyd-fancy-ui'):
            run('git clone https://%s:%s@github.com/%s/scrapyd-fancy-ui.git' % (username, password, username))
            move_scrapyd_configs(db_number)

def ask_data():
    username = prompt('1/3. Username of github:')
    password = getpass.getpass('2/3. Password of github:')
    valid = False
    while not valid:
        MIN_REDIS_DB_NUMBER = 1
        MAX_REDIS_DB_NUMBER = 9
        db_number = prompt("3/3. Your Redis database number: (%s-%s)" % (MIN_REDIS_DB_NUMBER, MAX_REDIS_DB_NUMBER))
        try:
            db_number = int(db_number)
            if db_number not in range(MIN_REDIS_DB_NUMBER, MAX_REDIS_DB_NUMBER):
                raise ValueError
            else:
                valid = True
        except ValueError:
            print "Please, enter a valid database number (from %s to %s)" % (MIN_REDIS_DB_NUMBER, MAX_REDIS_DB_NUMBER)
    return username, password, db_number

@task
def install():
    install_scraper()
    install_graphite()
    install_statsd()
    install_grafana()

@task
def install_scraper():
    '''
    Installs Python Scraper and dependencies
    '''
    
    print '------------------------------------------------'
    print "Welcome to the installer of the MyTaste Scraper"
    print '------------------------------------------------'
    print 'First of all, we need some information about your specific configuration to build your environment.\n'
    username, password, db_number = ask_data()

    _download_projects(username, password, db_number)

    sudo('yum -y upgrade')
    sudo('yum -y groupinstall "Development tools"')
    sudo('yum -y install wget zlib-devel bzip2-devel ncurses-devel libxml2 libxml2-dev libxslt libxslt-devel mysql-server mysql-devel sqlite-devel redis')
    sudo('yum -y install gcc libffi-devel openssl-devel python-devel')
    #Running redis
    sudo('service redis start')
    
    #Installing python 2.7
    if not exists('/usr/bin/python2.7'):
        run('mkdir -p /home/vagrant/src')
        with cd('/home/vagrant/src'):
            run('wget --no-check-certificate https://www.python.org/ftp/python/2.7.7/Python-2.7.7.tar.xz')
            run('tar xf Python-2.7.7.tar.xz')
        with cd('/home/vagrant/src/Python-2.7.7'):
            sudo('./configure --prefix=/usr')
            sudo('make && make altinstall')
        with cd('/home/vagrant'):
            run('echo "alias python=/usr/bin/python2.7" >> .bashrc')
            run('source .bashrc')
    #Installing pip
    with cd('/home/vagrant/src'):
        run('wget https://bootstrap.pypa.io/ez_setup.py')
        sudo('/usr/bin/python2.7 ez_setup.py')
        run('wget https://bootstrap.pypa.io/get-pip.py')
        sudo('/usr/bin/python2.7 get-pip.py')

    #Installing dependencies of the project
    put(scrapy_file('requeriments.txt'), '/home/vagrant/src/', use_sudo=True)
    with cd('/home/vagrant/src'):
        sudo('pip install -r requeriments.txt')

@task
def scrapyd(action):
    if action in ('start', 'stop', 'restart'):
        if action == 'start':
            with cd('/vagrant/scrapyd-fancy-ui'):
                run('twistd -ny extras/scrapyd.tac &')
    else:
        print "the parameter has to be 'start', 'stop' or 'restart'"

"""
 ===========================
    Graphite installation
 ===========================
"""
@task
def install_graphite():
    """
    Installs Graphite and dependencies
    """
    sudo('pip install supervisor simplejson') # required for django admin
    sudo('mkdir -p /opt/graphite')
    sudo('chmod 777 -R /opt')
    sudo('pip install git+https://github.com/graphite-project/carbon.git@0.9.x#egg=carbon')
    sudo('pip install git+https://github.com/graphite-project/whisper.git@master#egg=whisper')
    sudo('pip install django==1.5.2 django-tagging uwsgi')
    sudo('pip install git+https://github.com/graphite-project/graphite-web.git@0.9.x#egg=graphite-web')

    # Downloading PCRE source (Required for nginx)
    with cd('/home/vagrant'):
        run('wget http://sourceforge.net/projects/pcre/files/pcre/8.33/pcre-8.33.tar.gz/download# -O pcre-8.33.tar.gz')
        run('tar -zxvf pcre-8.33.tar.gz')

    # creating nginx etc and log folders
    sudo('mkdir -p /etc/nginx')
    sudo('mkdir -p /var/log/nginx')
    sudo('chmod 777 -R /etc/nginx')
    sudo('chmod 777 -R /var/log/nginx')
    sudo('chown -R vagrant: /var/log/nginx')

    # creating automatic startup scripts for nginx and carbon
    put(graphite_file('nginx'), '/etc/init.d/', use_sudo=True)
    put(graphite_file('carbon'), '/etc/init.d/', use_sudo=True)
    sudo('chmod ugo+x /etc/init.d/nginx')
    sudo('chmod ugo+x /etc/init.d/carbon')
    put(graphite_file('glyph.py'), '/opt/graphite/webapp/graphite/render', use_sudo=True)
    sudo('chkconfig nginx on')
    sudo('chkconfig carbon on')

    # downloading nginx source
    with cd('/home/vagrant'):
        run('wget http://nginx.org/download/nginx-1.2.7.tar.gz')
        run('tar -zxvf nginx-1.2.7.tar.gz')

    # installing nginx
    with cd('/home/vagrant/nginx-1.2.7'):
        sudo('./configure --prefix=/usr --with-pcre=/home/vagrant/pcre-8.33/ --with-http_ssl_module --with-http_gzip_static_module --conf-path=/etc/nginx/nginx.conf --pid-path=/var/run/nginx.pid --lock-path=/var/lock/nginx.lock --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --user=vagrant --group=vagrant')
        sudo('make && make install')

    # copying nginx and uwsgi configuration files
    sudo('mkdir -p /etc/supervisor/conf.d/')
    put(graphite_file('nginx.conf'), '/etc/nginx/', use_sudo=True)
    put(graphite_file('supervisord.conf'), '/etc/supervisord.conf', use_sudo=True)
    put(graphite_file('uwsgi.conf'), '/etc/supervisor/conf.d/', use_sudo=True)
    sudo('yum install -y libpng-devel pixman pixman-devel cairo pycairo')
    
    
    sudo('echo "/usr/lib" > /etc/ld.so.conf.d/pycairo.conf')
    sudo('ldconfig')
    # setting the carbon config files (default)
    with cd('/opt/graphite/conf/'):
        sudo('cp carbon.conf.example carbon.conf')
        put(graphite_file('storage-schemas.conf'), 'storage-schemas.conf')
    # clearing old carbon log files
    put(graphite_file('carbon-logrotate'), '/etc/cron.daily/', use_sudo=True, mode=0755)

    # initializing graphite django db
    with cd('/opt/graphite/webapp/graphite'):
        sudo("/usr/bin/python2.7 manage.py syncdb")

    # changing ownership on graphite folders
    sudo('chown -R vagrant: /opt/graphite/')

    # starting uwsgi
    run('supervisord')
    run('supervisorctl update && supervisorctl restart uwsgi')

    # starting carbon-cache
    sudo('/etc/init.d/carbon start')

    # starting nginx
    sudo('nginx')

"""
 ===========================
    Statsd installation
 ===========================
"""
@task
def install_statsd():
    """
    Installs etsy's node.js statsd and dependencies
    """
    sudo('yum install -y build-essential supervisor make git-core')
    with cd('/home/vagrant'):
        run('wget -N http://nodejs.org/dist/node-latest.tar.gz')
        run('tar -zxvf node-latest.tar.gz')
        sudo('cd `ls -rd node-v*` && make install')

    with cd('/opt'):
        run('git clone https://github.com/etsy/statsd.git')

    with cd('/opt/statsd'):
        run('git checkout v0.7.1') # or comment this out and stay on trunk
        put(statsd_file('localConfig.js'), 'localConfig.js', use_sudo=True)
        run('npm install')
    put(statsd_file('statsd.conf'), '/etc/supervisor/conf.d/', use_sudo=True)
    sudo('supervisorctl update && supervisorctl start statsd')

    # UDP buffer tuning for statsd
    sudo('mkdir -p /etc/sysctl.d')
    put(statsd_file('10-statsd.conf'), '/etc/sysctl.d/', use_sudo=True)
    sudo('sysctl -p /etc/sysctl.d/10-statsd.conf')

"""
 ===========================
    Grafana installation
 ===========================
"""

@task
def install_grafana():
    """
    Installs Grafana
    """
    with cd('/home/vagrant'):
        run('wget http://grafanarel.s3.amazonaws.com/grafana-1.6.0.tar.gz')
        run('tar -xzvf grafana-1.6.0.tar.gz')
        sudo('mv grafana-1.6.0/ /opt/grafana')
    with cd('/opt/grafana'):
        put(grafana_file('config.js'), 'config.js', use_sudo=True)

    sudo('nginx -s reload')


def install_elasticsearch():
    sudo('yum install -y java-1.7.0-openjdk java-1.7.0-openjdk-devel')
    with cd('/home/vagrant'):
        run('wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.2.1.noarch.rpm')
        sudo('rpm -iv elasticsearch-1.2.1.noarch.rpm')
    sudo('service elasticsearch start')

