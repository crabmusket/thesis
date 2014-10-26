# Effect of rho.
for r in 0.000000001,1 0.000000005,1.5 \
	      0.00000001,2 0.00000005,2.5 \
			0.0000001,3 0.0000005,3.5 \
			0.000001,4 0.000005,4.5; do
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
