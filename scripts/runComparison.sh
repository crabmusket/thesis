for d in 12,1 12,20 1,1 1,20 6,1 6,20 7,1 7,20; do
	IFS=","
	set $d
	for m in mpc thermostat; do
		python -m code.experiments.$m \
			--month $1 --day $2 \
			--days 7 \
			--start 3 --end 3 \
			--width 9 --height 6.5 \
			--horizon 8 \
			--cost 0.0000005 \
			report/results/$m-comparison-$1-$2
	done
done
