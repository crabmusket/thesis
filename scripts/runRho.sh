# Effect of rho.
for r in 0.01 0.05 1 10 20; do
	python -m code.experiments.mpc \
		--month 6 --day 1 \
		--days 7 --start 2 --end 3 \
		--width 7 --height 5 \
		--horizon 8 \
		--cost $r \
		report/results/mpc-rho-$r
done
