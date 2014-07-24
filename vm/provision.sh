cd /vagrant/vm

## Tools
echo "============== INSTALLING TOOLS"
apt-get update > /dev/null
apt-get install \
	git \
	python-software-properties \
	software-properties-common \
	-y

# TexLive
echo "============== INSTALLING TEXLIVE"
add-apt-repository ppa:texlive-backports/ppa -y
apt-get update > /dev/null
apt-get install \
	texlive \
	texlive-base \
	#texlive-full \
	texlive-latex-extra \
	texlive-bibtex-extra \
	pgf \
	-y
apt-get upgrade -y > /dev/null

# Components
./setup-python.sh
./setup-node.sh

# Startup script
cp ./thesis-viewer.conf /etc/init/thesis-viewer.conf
