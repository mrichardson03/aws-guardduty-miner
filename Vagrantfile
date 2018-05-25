# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|

  config.vm.define "minemeld" do |minemeld|
    minemeld.vm.box = "geerlingguy/ubuntu1604"
    minemeld.vm.hostname = "minemeld"
    minemeld.vm.network "forwarded_port", guest:443, host: 8443

    minemeld.vm.provider "virtualbox" do |vb|
      vb.cpus = "2"
      vb.memory = "4096"
    end

    minemeld.vm.provision "file", source: "./utils/loadext.sh", destination: "/home/vagrant/loadext.sh"
    minemeld.vm.provision "file", source: "./utils/unloadext.sh", destination: "/home/vagrant/unloadext.sh"

    minemeld.vm.provision "shell", inline: <<-SHELL
      sudo apt-get update
      sudo apt-get upgrade
      sudo apt-get install -y gcc git python-minimal python2.7-dev libffi-dev libssl-dev make
      wget https://bootstrap.pypa.io/get-pip.py
      sudo -H python get-pip.py
      sudo -H pip install ansible
      git clone https://github.com/PaloAltoNetworks/minemeld-ansible.git
      cd minemeld-ansible
      ansible-playbook -K -i 127.0.0.1, local.yml
      sudo usermod -a -G minemeld vagrant
      chmod u+x /home/vagrant/loadext.sh
      chmod u+x /home/vagrant/unloadext.sh
    SHELL

    minemeld.vm.synced_folder "./dist", "/opt/minemeld/local/library/gd"
  end
end
