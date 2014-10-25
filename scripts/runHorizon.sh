# Effect of time horizon.
for H in 4 6 8 10 12; do
	python -m code.experiments.mpc \
		--month 6 --day 1 \
		--days 7 --start 2 --end 3 \
		--width 7 --height 5 \
		--horizon $H \
		report/results/mpc-horizon-$H
done
