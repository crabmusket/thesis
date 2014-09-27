echo "============== INSTALLING PYTHON DEPEPDENCIES"
apt-get build-dep python-scipy matplotlib -y
apt-get install python-dev python-pip libagg-dev -y

pip install distribute --upgrade
pip install numpy==1.8.1 \
            scipy==0.14.0 \
            matplotlib==1.3.1

if ! $(python -c "import setuptools" &> /dev/null); then
	echo "============== INSTALLING SETUPTOOLS"
	wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python
	rm ./setuptools-3.5.1.zip
fi

if ! $(python -c "import slycot" &> /dev/null); then
	echo "============== INSTALLING SLICOT"
	git clone git://github.com/avventi/Slycot.git
	cd Slycot
	git checkout 5af5f283
	python setup.py install
	cd ..
	rm -r Slycot
fi

if ! $(python -c "import control.matlab" &> /dev/null); then
	echo "============== INSTALLING PYTHON-CONTROL"
	wget http://sourceforge.net/projects/python-control/files/control-0.6d.tar.gz/download -O control-0.6d.tar.gz
	tar xzf control-0.6d.tar.gz
	rm control-0.6d.tar.gz
	cd control-0.6d
	python setup.py install
	cd ..
	rm -r control-0.6d
fi

echo "============== INSTALLING CVXPY"
pip install cvxpy==0.2
