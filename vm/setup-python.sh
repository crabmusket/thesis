## Install scipy, numpy, etc.
apt-get install python-pip libagg-dev libatlas-base-dev gfortran -y > /dev/null
pip install scipy==0.14.0 > /dev/null
pip install matplotlib==1.3.1 > /dev/null

if [ $(python -c "import setuptools" &> /dev/null) ]; then
	# Python setup
	wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python > /dev/null
	rm ./setuptools-3.5.1.zip
fi

if [ $(python -c "import control.matlab" &> /dev/null) ]; then
	## Install SLICOT wrapper
	git clone git://github.com/avventi/Slycot.git
	cd Slycot
	git checkout 5af5f283
	python setup.py install > /dev/null
	cd ..
	rm -r Slycot

	## Install python-control library
	wget http://sourceforge.net/projects/python-control/files/control-0.6d.tar.gz/download -O control-0.6d.tar.gz
	tar xzf control-0.6d.tar.gz
	rm control-0.6d.tar.gz
	cd control-0.6d
	python setup.py install > /dev/null
	cd ..
	rm -r control-0.6d
fi

# cvxpy
pip install cvxpy==0.2 > /dev/null
