sudo apt-get update

## Tools
sudo apt-get install git python-pip -y
wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python

## Install scipy, numpy, etc.
sudo apt-get build-dep python-scipy -y
sudo apt-get install python-scipy libagg-dev python-matplotlib -y

## SLICOT
git clone git://github.com/avventi/Slycot.git
cd Slycot
sudo python setup.py install
cd ..
rm -r Slycot

## python-control
wget http://sourceforge.net/projects/python-control/files/control-0.6d.tar.gz/download -O control-0.6d.tar.gz
tar xzf control-0.6d.tar.gz
rm control-0.6d.tar.gz
cd control-0.6d
sudo python setup.py install
cd ..
rm -r control-0.6d

# cvxpy
sudo pip install cvxpy
