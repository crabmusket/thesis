set terminal png enhanced
set output "report/images/rho-graphs.png"
set xlabel " "
set logscale x
set format x "%.0e"
set xrange [5e-9:1e-5]
plot "report/results/rho.txt" using 1:2 with lines title "Satisfaction (%)", \
	  "report/results/rho.txt" using 1:3 with lines title "Total energy (kWh)", \
	  "report/results/rho.txt" using 1:4 with lines title "Solar contribution (%)"
