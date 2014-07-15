Instalacion del entorno del Scraper.

The scraper is basically a mix of two tools: The scraper itself (made with Scrapy) and the daemon that maintain the service, called Scrapyd. In order to install this project easily, we have prepared this bolierplate.

Prerequisites:

To install the environment we need basically three tools: Virtualenv, Vagrant and Fabric

Virtualenv: Virtualenv is an open-source virtual machine which is used by Vagrant to build our project.

Vagrant:

Vagrant is a virtual machine manager with a lot of functionallities related to this. To install it, just go to the official webpage http://www.vagrantup.com.

Fabric:

Fabric is a library for executing Bash commands in Python. To install it, we firstly need to have installed pip (Python Package Index). To install it follow the steps of the official webpage: https://pip.pypa.io/en/latest/installing.html . Once installed, we have simply to execute this command to install Fabric:

pip install fabric fabtools

We need 'fabtools' too to give compatibility to Vagrant

Instalation:

First of all, we have to download the configuration project:

git clone https://github.com/ivangoblin/scraper-boilerplate

Now we just have to execute these commands:

vagrant box add centos https://github.com/2creatives/vagrant-centos/releases/download/v6.5.3/centos65-x86_64-20140116.box

vagrant up

fab vagrant install
