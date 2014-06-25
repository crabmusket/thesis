cd /vagrant/vm

## Tools
apt-get update > /dev/null
apt-get install git -y > /dev/null
apt-get install python-software-properties -y

# TexLive
add-apt-repository ppa:texlive-backports/ppa -y
apt-get update > /dev/null
apt-get install \
	texlive \
	texlive-base \
	texlive-common \
	texlive-full \
	texlive-latex-extra \
	-y > /dev/null
apt-get upgrade -y > /dev/null

# Components
./setup-python.sh
./setup-node.sh

# Startup script
cp ./thesis-viewer.conf /etc/init/thesis-viewer.conf
