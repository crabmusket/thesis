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
	mkdir build
	cd build
	cmake ..
	make
	cd ../..
fi
