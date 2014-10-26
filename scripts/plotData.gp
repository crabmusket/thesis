set terminal png enhanced
set output "report/images/insolation-prediction.png"
set xlabel "Time (hours)"
set ylabel "Insolation (100 MJ/hour)"
plot "data/insolation2.txt" every ::3624::3672 using 1 with steps title "Indirect", \
	  "data/insolation2.txt" every ::3624::3672 using 2 with steps title "Direct"

set output "report/images/insolation-actual.png"
set xlabel "Time (hours)"
set ylabel "Insolation (100 MJ/hour)"
plot "data/insolation.txt" every ::3624::3672 using 1 with steps title "Indirect", \
	  "data/insolation.txt" every ::3624::3672 using 2 with steps title "Direct"
