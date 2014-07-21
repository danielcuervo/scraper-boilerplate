# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "centos"
  config.vm.synced_folder "/var/log/scrapyd/", "/var/log/scrapyd/"
  config.vm.network :forwarded_port, guest: 6800, host: 6800
  config.vm.provider "virtualbox" do |v|
  	v.memory = 2048
  end
end
