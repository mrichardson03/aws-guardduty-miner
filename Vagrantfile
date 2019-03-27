# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|

  config.vm.define "minemeld" do |minemeld|
    minemeld.vm.box = "bento/ubuntu-16.04"
    minemeld.vm.hostname = "minemeld"
    minemeld.vm.network "forwarded_port", guest: 443, host: 8443

    minemeld.vm.provider "virtualbox" do |vb|
      vb.cpus = "2"
      vb.memory = "4096"
    end

    config.vm.provider :vmware_desktop do |v|
      v.vmx["numvcpus"] = "2"
      v.vmx["memsize"] = "4096"
    end

    minemeld.vm.provision "shell", inline: <<-SHELL
      sudo apt-get update
      sudo apt-get upgrade -y
      wget -qO - https://minemeld-updates.panw.io/gpg.key | sudo apt-key add -
      sudo add-apt-repository "deb http://minemeld-updates.panw.io/ubuntu xenial-minemeld main"
      sudo apt-get update
      sudo apt-get install -y nginx redis-server
      sudo apt install -o Dpkg::Options::="--force-overwrite" -y minemeld
    SHELL
  end
end
