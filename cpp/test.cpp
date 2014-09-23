#include <acado_toolkit.hpp>
#include <include/acado_gnuplot/gnuplot_window.hpp>

int main() {
   USING_NAMESPACE_ACADO;

   // System parameters.
   double L = 1.0,
          m = 1.0,
          g = 9.81,
          b = 0.2;

   // Equations.
   DifferentialState x,
                     v,
                     phi,
                     dphi;
   Control ax;

   DifferentialEquation f;
   f << dot(x) == v;
   f << dot(v) == ax;
   f << dot(phi) == dphi;
   f << dot(dphi) == -g/L*sin(phi) - ax/L*cos(phi) - b/(m*L*L)*dphi;

   // Not sure what this bit does yet.
   Function h;
   h << x;
   h << v;
   h << phi;
   h << dphi;

   Matrix Q(4, 4);
   Q.setIdentity();

   Vector r(4);

   double t0   =   0.0;
   double tf   =   5.0;

   OCP ocp(t0, tf, 25);
   ocp.minimizeLSQ(Q, h, r);
   ocp.subjectTo(f);
   ocp.subjectTo(-5.0 <= ax <= 5.0);

   OutputFcn identity;
   DynamicSystem system(f, identity);
   Process process(system, INT_RK45);
   RealTimeAlgorithm alg(ocp, 0.1);
   StaticReferenceTrajectory ref;
   Controller controller(alg, ref);
   SimulationEnvironment sim(0, 20, process, controller);

   Vector x0(4);
   x0.setZero();
   x0(3) = 5;

   sim.init(x0);
   sim.run();

   VariablesGrid states, control;
   sim.getProcessDifferentialStates(states);
   sim.getFeedbackControl(control);
   states.printToFile("states.txt");
   control.printToFile("control.txt");

   return 0;
}
