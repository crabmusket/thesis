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
