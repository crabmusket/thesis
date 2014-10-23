set terminal png enhanced
set output "../report/images/insolation-prediction.png"
set xlabel "Time (hours)"
set ylabel "Insolation (100 MJ/hour)"
plot "insolation2.txt" every ::3624::3672 using 1 with lines title "Indirect", \
	  "insolation2.txt" every ::3624::3672 using 2 with lines title "Direct"

set output "../report/images/insolation-actual.png"
set xlabel "Time (hours)"
set ylabel "Insolation (100 MJ/hour)"
plot "insolation.txt" every ::3624::3672 using 1 with lines title "Indirect", \
	  "insolation.txt" every ::3624::3672 using 2 with lines title "Direct"
