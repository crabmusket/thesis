# Effect of rho.
for r in 0.00001,5.1 0.00005,5.5 \
			0.0001,6.1 0.0005,6.5; do
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
