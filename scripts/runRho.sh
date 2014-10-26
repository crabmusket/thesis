# Effect of rho.
for r in 0.000000001,19 0.000000005,59 \
			0.00000001,18	0.00000005,58 \
			0.0000001,17	0.0000005,57 \
			0.000001,16		0.000005,56 \
			0.00001,15		0.00005,55 \
			0.0001,14		0.0005,54 \
			0.001,13		   0.005,53 \
			0.01,12		   0.05,52; do
	IFS=","
	set $r
	python -m code.experiments.mpc \
		--month 6 --day 1 \
		--days 1 \
		--width 9 --height 6.5 \
		--horizon 8 \
		--cost $1 \
		report/results/mpc-rho-$2
done
