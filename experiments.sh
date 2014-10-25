# Effect of prediction error (overpredicting insolation).
python -m code.experiments.mpc \
	--days 7 \
	--start 2 --end 2 \
	--width 7 --height 5 \
	--insolationP data/insolation2.txt \
	--internals \
	report/results/mpc-prediction-error

python -m code.experiments.mpc \
	--days 7 \
	--start 2 --end 2 \
	--width 7 --height 5 \
	--internals \
	report/results/mpc-prediction-noerror
