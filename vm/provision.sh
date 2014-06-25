cd /vagrant/vm

## Tools
apt-get update > /dev/null
apt-get install git -y > /dev/null
apt-get install texlive-full -y > /dev/null

# Components
./setup-python.sh
./setup-node.sh

# Startup script
cp ./thesis-viewer.conf /etc/init/thesis-viewer.conf
