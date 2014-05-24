cd /vagrant/vm

## Tools
apt-get update
apt-get install git -y

# Components
./setup-python.sh
./setup-node.sh

# Startup scripts
cp startup-node.sh /etc/init.d/
chmod +x /etc/init.d/startup-node.sh
update-rc.d startup-node.sh defaults
