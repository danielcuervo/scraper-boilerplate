#!/usr/bin/env python
 # -*- coding: utf-8 -*-

from vagrant import vagrant
from fabric.api import cd, sudo, run, put, settings, task, local
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

def move_scrapy_configs():
    with cd('/vagrant/python-scraper'):
        put(scrapy_file('processes_settings.py'), 'processes/settings.py')
        put(scrapy_file('scraper_settings.py'), 'py203scraper/settings.py')
        put(scrapy_file('scrapy_settings.cfg'), 'scrapy.cfg')

def move_scrapyd_configs(db_number):
    with cd('/vagrant/'):
        run('cp config/scrapyd/scrapyd.conf scrapyd-fancy-ui/scrapyd.conf')
        s = open('scrapyd-fancy-ui/scrapyd.conf').read()
        s = s.replace('{{REDIS_DB_NUMBER}}', str(db_number))
        f = open('scrapyd-fancy-ui/scrapyd.conf', 'w')
        f.write(s)
        f.close()

def _download_projects(username, db_number):
    with cd('/vagrant'):
        if not exists('/vagrant/python-scraper') or not exists('/vagrant/scrapyd-fancy-ui'):
            print "In order to download the scraper repository, we need your username to continue."
        if not exists('/vagrant/python-scraper'):
            run('git clone https://%s@github.com/%s/python-scraper.git' % (username, username) )
            move_scrapy_configs()
        if not exists('/vagrant/scrapyd-fancy-ui'):
            run('git clone https://%s@github.com/%s/scrapyd-fancy-ui.git' % (username, username))
            move_scrapyd_configs(db_number)

def ask_data():
    username = prompt('1/2. Username of github:')
    valid = False
    while not valid:
        MIN_REDIS_DB_NUMBER = 1
        MAX_REDIS_DB_NUMBER = 9
        db_number = prompt("2/2. Your Redis database number: (%s-%s)" % (MIN_REDIS_DB_NUMBER, MAX_REDIS_DB_NUMBER))
        try:
            db_number = int(db_number)
            if db_number not in range(MIN_REDIS_DB_NUMBER, MAX_REDIS_DB_NUMBER):
                raise ValueError
            else:
                valid = True
        except ValueError:
            print "Please, enter a valid database number (from %s to %s)" % (MIN_REDIS_DB_NUMBER, MAX_REDIS_DB_NUMBER)
    return username, db_number

def cleanup():
    sudo('rm -rf /home/vagrant/src')

@task
def install():
    '''
    Installs Python Scraper and dependencies
    '''
    
    print '------------------------------------------------'
    print "Welcome to the installer of the MyTaste Scraper"
    print '------------------------------------------------'
    print 'First of all, we need some information about your specific configuration to build your environment.\n'
    username, db_number = ask_data()

    local('sudo mkdir -p /var/log/scrapyd')

    _download_projects(username, db_number)
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

    sudo('mkdir -p /var/log/scrapyd')
    sudo('chmod 777 /var/log/scrapyd')

    cleanup()

@task
def up():
    sudo('service redis start')
