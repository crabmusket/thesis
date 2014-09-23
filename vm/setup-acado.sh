apt-get install \
	gcc g++ \
	cmake \
	gnuplot graphviz \
	-y

if ! $(cd acado/examples/getting_started && ./simple_ocp); then
	echo "============== INSTALLING ACADO"
	cd /vagrant/vm
	git clone https://github.com/acado/acado.git -b stable
	cd acado
	# Ensure consistent version
	git checkout 1bd15b235f94b7696f3429675c8b56fc2ecc9627
	mkdir build
	cd build
	cmake ..
	make
	cd ../..
fi
