apt-get install python-pip -y

## Install scipy, numpy, etc.
apt-get build-dep python-scipy -y
apt-get install python-scipy libagg-dev python-matplotlib -y

if [ $(python -c "import setuptools" &> /dev/null) ]; then
	wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python
	rm ./setuptools-3.5.1.zip
fi

if [ $(python -c "import control.matlab" &> /dev/null) ]; then
	## Install SLICOT wrapper
	git clone git://github.com/avventi/Slycot.git
	cd Slycot
	python setup.py install
	cd ..
	rm -r Slycot

	## Install python-control library
	wget http://sourceforge.net/projects/python-control/files/control-0.6d.tar.gz/download -O control-0.6d.tar.gz
	tar xzf control-0.6d.tar.gz
	rm control-0.6d.tar.gz
	cd control-0.6d
	python setup.py install
	cd ..
	rm -r control-0.6d
fi

# cvxpy
pip install cvxpy
