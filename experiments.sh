# Effect of prediction error (overpredicting insolation).
for f in insolation.txt,noerror insolation2.txt,error; do
	IFS=","
	set $f
	python -m code.experiments.mpc \
		--month 5 --day 31 \
		--days 8 --start 3 --end 3 \
		--width 7 --height 5 \
		--insolationP data/$1 \
		--internals \
		report/results/mpc-prediction-$2
done

# Effect of time horizon.
for H in 4 6 8 10 12; do
	python -m code.experiments.mpc \
		--month 6 --day 1 \
		--days 7 --start 2 --end 3 \
		--width 7 --height 5 \
		--horizon $H \
		report/results/mpc-horizon-$H
done

# Effect of rho.
for r in 0.1 0.5 1 5 10; do
	python -m code.experiments.mpc \
		--month 6 --day 1 \
		--days 7 --start 2 --end 3 \
		--width 7 --height 5 \
		--horizon 8 \
		--cost $r \
		report/results/mpc-rho-$r
done
