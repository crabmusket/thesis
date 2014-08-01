# Summaries

## Grant08

### Introduction and final words

 * There are general convex program solvers and specialised ones that exploit
   aspects of problem definition or structure.
 * General solvers may be efficient in theory, but not in practise.
 * Specialised solvers require that the problem is transformed into some
   _standard form_ that they can solve.
 * Transformation may be obscure, difficult, and error-prone, even for experts.
 * Transformed problem may be larger (e.g. more constraints, free variables)
   but the solver may still be more efficient because of the problem structure.
 * These transformations are desirable and useful!
 * These transformations can be _automated_.
 * Experienced optimisation practitioners tend to construct programs from
   known convex functions ('atoms') and operations that combine them while
   preserving their convexity. Disciplined convex programming formalises this
   method.
 * Using graph methods, experts can implement automatic transformations of
   problems to standard form of many different solvers.
 * Non-expert and application-focused users are presented with an easy
   interface for expressing convex programs.
 * Separation of concerns.
 * "Closes the gap between convex optimisation theory and practise"

### DCP

 * Provides a ruleset for combining convex expressions.
 * Provides a 'library' of _atoms_ that are known to be convex.
 * Atoms are often expressed as extended-value equivalents of common functions.
   For example, `sqrt x | x < 0 = -∞`.
 * DCP requires users to provide "just enough structure" for the program to
   automatically transform it. For example, `sqrt . sum . square` is not valid
   due to DCP's function composition rules, even though it is numerically the
   same as the atom `norm`.
 * Therefore the DCP ruleset is sufficient for convexity, but not necessary
   (i.e. come convex expressions may not be valid DCP expressions).

### Graph implementations

 * A convex function has a convex epigraph, therefore finding the infimum of the
   epigraph solves the function. Thus atoms can be expressed as simple
   optimisation problems on the epigraph.
 * Same for concave functions with the hypograph.
 * Sub-problems are 'inlined' into the user's desired problem.
 * Introduces more variables and constraints, but the use of more efficient
   solvers. Tends to be beneficial in practise.

## Siroky10

### Introduction

 * Building climate control accounts for a large amount of first-world energy
   expenditure.
 * BAS can control not only HVAC but also blinds and lighting.
 * Thermal mass is important to consider when heating/cooling a building and
   critical to the MPC problem.
 * Different energy rates (i.e. nighttime) should also be taken into account by
   the control strategy.

### MPC

 * MPC is typically used to control high-level setpoints, with per-room
   controllers ensuring those setpoints are maintained.
 * Aim to minimise the electricity bill while meeting comfort constraints.
 * Stability is often a non-issue for building control.
 * Objective function minimises difference from a trajectory using a quadratic
   form to penalise deviation.
 * Energy bill is usually an _affine_ function of the control effort.
 * Peak energy demand can be penalised using the L∞ norm.

### Modeling

 * Actual models (e.g. Simulink or TRNSYS) cannot be used to formulate control
   strategies using optimisation, and are slow to solve, so RC modelling is
   typically used instead.
 * Once an RC model structure is derived, its properties can be filled in using
   statistical identification or _a priori_ knowledge of the materials and
   construction.

### Case study

 * Building layout (three identical blocks) gave good opportunity to compare
   strategies with identical weather conditions, and with different insulation
   conditions.
 * A/B study where one block was controlled by fixed curves and others by MPC.
 * Reference trajectory is known, dictated by daytime/nighttime setpoints in
   each room.
 * Comfort is used not as a constraint (may lead to infeasible problem) but
   penalised in cost function (only negative difference penalised).
 * Q and R in cost function constant, since energy rate is flat, but had to be
   tuned per-block.
 * Lower limit of control input depends on return water temperature but this
   effect was neglected.
 * H = 2 days, δt = 20 min
 * QP solve time: 21s on 2x2.5GHz
 * Backup strategy in case network comms or other software failed.
 * Two comparisons: cross-comparison of blocks under different control, and
   comparison of HDD (heating degree days) for two blocks in similar external
   conditions.
 * Saved from 15% to 28% of energy bill. Relative savings larger in insulated
   block, but absolute savings larger in uninsulated block.
 * MPC savings depend on many building-specific factors.
 * Cost/benefit analysis should include cost of model development and integration.

## Fitzmorris10

### Porter's five forces

 * Water heating is the second-largest use of domestic power.
 * Solar water heating has been losing domestic market share.
 * Cost: $300 for electric heating system or $2000 for solar system.
 * Builders sensitive to price and often go for the cheaper option.
 * Homeowners replacing a broken system influenced by speed of replacement, which
   is worse for solar systems as they require sizing and installation.
 * In the past, systems were sized for winter, leading to overheating in summer
   and requiring more maintenance.
 * Two key forces preventing adoption: price sensitivity and distribution channels.
 * Solar thermal regarded as best system w.r.t. energy consumption.
 * Contractors not really providing them so builders and homeowners cannot access
   them as readily.

### Technology lifecycle

 * Low, medium (flat plate/evacuated tube/ICS) and high-temperature systems.
 * Low-temperature poised to cross chasm.
 * Very cost-competitive when compared to gas pool heater, though requires additional
   space for collectors.
 * Medium and high tech still disruptive despite higher initial cost and lower
   performance (compare to digital cameras).
 * Evacuated tube may become domniant medium-temp technology if price decreases.
 * Recommends bundling multiple technologies/services/products in a sales pitch
   to make adoption attractive. "Home energy services"
 * Solar Power Purchase Agreement: customer pays a price for energy generated by
   the system in return for reduced or eliminated up-front costs.
 * Hot water systems cannot take advantage of grid feed-in tariffs.

## Ma12

### Intro

 * Building sector consumes 40% of energy.
 * Efficiency of control depends on 'active storage of thermal energy'.
 * Campus cold water storage enables load-shifting to off-peak time, but tank is
   often over-charged. Heat loss reduces efficiency.
 * MPC controller ensures the tank always has enough water given uncertain
   load requirements.

### Model and MPC formulation

 * Stratified (2-layer) tank model. Actual tank formed a second thermocline that
   was ignored for model simplicity.
 * Campus load modelled with RC network accounting for wall and window thermal
   masses, thermal loads from people, lights, equipment, as well as ambient
   temperature, sunlight, etc.
 * Weather prediction used to predict campus load.
 * Mass flow rate of chilled water (input) is non-convex binary set, but depends
   on start/finish time of chilling sequence, which are chosen as optimisation
   variables (assumed).
 * Prediction horizon 24 hours, sampling time 1 hour.
 * Move blocking strategy reduces problem size.
 * Terminal constraints for stability.
 * Historical disturbance data used to construct terminal constraint set to
   guaranteee robustness (i.e. there will be enough water in the tank).

### Results

 * Four trials: manual control, MPC with some restriction, manual control after
   seeing MPC, and full MPC.
 * Full MPC did the best, increasing COP by 19% and reducing daily bill by 76%.
 * MPC strategy was very similar to manual strategy in general, but numbers tuned
   to increase chiller efficiency and not overload the towers.
 * Over a range of weather conditions in a 6 month simulation, MPC consistently
   outperformed manual control.
 * Performed best at ambient temperatures of 285 to 291K.

## Cristofari02

### Intro and description

 * Countries want to reduce their oil dependence (since 1973!).
 * France is putting emphasis on nuclear power; Corsica is diversifying.
 * Solar installations are not yet price-competitive.
 * Greece is introducing political incentives that increase competitiveness.
 * This paper invstigates new materials that might make a solar collector more
   affortable without sacrificing performance.
 * Collector installation cost: 20%, material cost: 80%, representing 50% of
   total solar system cost. This is high.
 * This paper develops a model of the collector taking material heat capacitance
   into account allowing simulation of the collector.

### Modeling

 * Stratified tank model with 10 nodes. Each node has uniform volume but
   changes in temperature.
 * Water entering the tank is put into a single node which has a density
   closest to its own, and then pushes water into adjacent nodes.
 * Two loops: upwards flow from load return, and downards flow from collector
   return.
 * Collector control function is defined as a binary function of the node index,
   temperautre in the node and in the entering water.
 * Collector and load control functions are integrated to derive the heat flow
   equation for each node at a specific flow rate.
 * Equations are solved using a matrix differential equation.

## Halvgaard12

### Experiment

 * 9sqm solar panel, 788L tank with stratifiers on inputs, 3x3kW heating elements.
 * Electricity prices vary, known 12 hours ahead. Weather forecast known 36 hours
   ahead.
 * Use heat flow model of tank, not explicit stratification model. Single
   temperature assumed to be average of 8 sensors.
 * Domestic load with even spikes at 7am, 12n, 7pm.
 * Parameter estimation (ML/MAP) used to derive state space model with noise.
 * Heating element efficiency fixed at η=1.

### Results

 * Annual savings around 25-30%.
 * Prediction horizon > 24 hrs did not have much effect on the savings.
 * Perfect forecasts did not have much effect on savings.
 * Power consumption tended to increase as prediction horizon lengthened, because
   energy was used at off-peak times.
 * Control is only active at the lower temperature bound.
 * When minimizing power consumption, prediction horizon had no effect due to
   sampling time (1h) being much longer than dynamics (~5min).
 * Milliseconds to solve MPC problem.

## Cao14

### Intro and design

 * Not so much research focused on replacing existing systems with SHWS.
 * Hot water _consumption_ is "high quantity but low quality" (like solar energy).
 * Differential temperature controllers used to circulate water in the collectors.

### Economics

 * System lifetime designed to be 20 years.
 * Considered cash inflow from carbon credits.
 * Analysed in terms of PTDA: practical to designed area, i.e. the difference in
   collector area from the system design to the actual installation.
 * With a PTDA of 1.0, the payback time was 7.4 years.
 * Over 20 years, _total_ investment in the solar system was less than the
   _initial_ investment in the GGS.

## Hollands89

### Intro and advantages

 * High flow changes the collector efficiency curve favourably, but stratification
   can move the operating point along the curve and achieve better results.
 * Improve "performance" by 38%.
 * Reduced cost of piping, heat exchange, and pumping.

### Modelling

 * Degradation of stratification due to conduction between layers takes several
   days and is usually ignored. Losses due to conduction with the side walls,
   however, may be significant.
 * Usually modelled by fixed-volume disks whose temperature/energy changes.
 * Systems down to 3 nodes underestimated solar output by up to 10%. Up to 64
   nodes were needed to properly model complex load/supply patterns.
 * It's not the flow rate that has so much affect as the stratification. High
   flow rate tends to destroy stratification, so low flow rates "look better".
   High flow rates could be used with good diffusers.

## Oldewurtel10

### MPC theory

 * Probabilistic cost function: minimise the chance of an event occurring, such
   as cost bounds being violated.
 * Linear system is most common, and the only one that results in a convex
   optimisation problem.
 * Input-affine model covers vast array of models, and was used in OptiControl
   by repeatedly linearising about the operating point.
 * Identified constraints as key benefit of MPC.
 * Robust MPC acknowledges that there may be several system trajectories for
   each input due to disturbances, and attempts to ensure the constraints hold
   on each of those possible trajectories.
 * Affine disturbance feedback MPC:
    * Sequence of future inputs _u_ and disturbances _w_.
    * Input at time _i_ depends on all prior disturbances, weighted by entries in
      matrix _M_. So _ui_ is an affine function of _M_, _w_ and _h_???
    * Optimise over _M_ instead of _u_.
    * Computation time can be reduced by restricting DOF of _M_ or replacing it
      with a weighted sum of precomputed matrices.
 * Disturbances are well-modelled as Gaussians, except that they have _infinite
   support_ - i.e. there is a small chance of an arbitrarily large disturbance
   happening. So there are no guarantees, actually.
 * Instead of constraining state, which we cannot therefore guarantee, we
   constrain the probability of a violation.
 * Europan standards specify comfort bounds in this way. Cool.
 * Performance bound could theoretically be calculated over an entire year at
   once, but since the bilinear system model required linearisation, that could
   not be done.

### Model and solver

 * Bilinear, two terms coming from the heat flow without considering the window,
   and with the window/blind position as an input (there is a term with _xu_).
 * SQP is used - repeatedly linearise system around current solution then solve
   QP, checking for a convergence.
 * 'Mild' nonlinearities and only linear programs once that's happened, not QPs.
 * Certainty equivalence constraints - just use the mean value of expected
   disturbances, and tighten the constraint bounds to provide robustness.
 * Chance constraints - ends up being the same as CE, but with margins determined
   somewhat mathematically. Or something. Apparently it's very conservative,
   especially with long prediction horizons.
 * SMPC - less conservative than CC. Uses _M_ as described in 'affine disturbance
   feedback' MPC. Results in SOCP. Pre-processed in OptiControl to avoid long
   calculations during runtime.
 * Cost functions: either non-renewable energy used, or total power bill.
   Minimised expected value.
 * 'Add variables' to allow constraints to be violated with heavy penalty, since
   constraints make for infeasible problems sometimes. Weight these penalties
   to design for relative importance of constraints.

### Discussion

 * MPC describes 'what' to achieve (minimise cost while satisfying comfort)
   instead of describing 'how' to do this. Like functional programming!
 * Does not need an expert... lol.
 * Easily adjust on-the-fly between weightings (just a linear combination).
 * Low-level controllers should be considered:
    * Derive controls with rule-based interpretation of MPC solutions.
    * Use next predicted temperature in MPC problem as set-point of low-level
      controller (PID or whatever).
    * Include low-level controller model in MPC problem and generate inputs
      at the planning stage.

## Vrettos12

### EWH modelling

 * First time an explicit detailed stratified model is developed _for use in
   load frequency control applications._
 * Trades some accuracy for reduced complexity.
 * Splits the tank into disks.
 * Accounts for internal heat generation at every particular location (i.e., the
   heat function is _Q(x, t)_).
 * One-dimensional PDE for heat flow in tank, reduced to a linear state-space
   model.
 * Natural convection is applied as a 'post-processing' step after the state-space
   model is applied at each timestep.
 * Validated from real measurements of a tank going through heating cycles.

### Population modelling

 * Probability distribution of tank sizes.
 * Minimum and maximum draw boundaries for each category of heater. Actual draw
   is a uniform distribution between these bounds.
 * Thermostat deadband and thermal loss coefficient come from uniform distributions
   (identical over all categories, it appears).
 * Model draws by choosing random start timne, duration, and rate from an existing
   probability distribution.
 * Choose a maximum number per day and multiply it over the probability each hour.
 * Water draws may be short or long. More likely to be long at peak times.
 * Flow rate comes from a normal distribution.

### State of charge

 * SOC is typically applied to batteries. EWHs store energy as well so we can
   define an SOC measurement for them as well.
 * Three different ideas developed:
    * Based on user perception or heating element: uses _T* - Tmin / Tmax - Tmin_
      where _T*_ is either the temperature at the element or at the point of use.
    * Based on temperature distribution: sums all temperatures relative to
      setpoints in each layer of the tank. Can result in SOC > 1, but not < 0.

### Control schemes

 * Four scenarios/strategies.
 * Control scenarios differ in two ways: degree of information known about each
   device, and degree to which the central controller can change each device's
   duty cycle.

 * C1 Stochastic blocking
    * Controller knows global population parameters (total load, desired setpoint,
      and maximum power demand) and calculates a percentage of the population to
      'block'.
    * Controller ignores internal control if blocked, but can choose whether to
      heat or not if not blocked.
    * Performed well in terms of number of switches and RMSE. However, almost 40%
      of devices spent half an hour of the day unable to match warm water demand.
    * Had periods of high tracking error on the real LFC signal.

 * C2 Direct temperature feedback
    * Controller knows on/off state and temperature (SOC?) of each EWH.
    * Divide controllers into sets of too cold, too hot, and _just right_, then
      decide on some control actions to take to turn them on and off.
    * Ranks EWHs based on difference between setpoint and average power of
      population.
    * Can override internal control signals.
    * Performs better when using SOC based on temperature distribution.
    * All performed okay, but with lots of switching, except variant _d_, which
      had very low switching and RMSE, but also low comfort properties.

 * C3 Indirect temperature feedback
    * The controller only knows when heaters' temperatures have crossed the
      setband limits, not their precise temperature.
    * Less communication overhead if events are sent when they happen.
    * Uses MPC? Estimates temperature based on historical data and model.
    * Respects internal controller?
    * Tracking quality isn't great.

 * Aggregate power feedback
    * Controller receives only aggregate power and setpoint information.
    * SOC limits are sent to all controllers, each of which uses this information
      to modify their internal control.
    * Resulted in very few switching actions.
    * Lower RMSE than C3 because it had smoother tracking without spikes.
    * Very good comfort properties.

 * Authors note that C2 is quite suitable. C1 no way, C3 and C4 for applications
   without strict tracking requirements (load shifting).
 * C4 has 'more acceptable overall performance' with the tradeoff of extra work
   (MPC) in the controller.

## Kondoh11

### Intro

 * Demand-side management is the least-studied and least-exploited response
   method for regulation.
 * DSM programs' telemetry requirements are blocking adoption.
 * Difficult to maintain user comfort if the 'load-shedding period is longer than
   the period for which the TCAs are capable of coasting' i.e. providing comfort
   without additional power expenditure.
 * Tariff control has a very complicated relationship with demand and may cause
   oscillations.
 * Since EWHs are storage, they can shift their demand rather than just reduce it.

### Tank model

 * Two fixed-volume layers with zero-width mixing layer.
 * Two heating elements, one for each layer.
 * Lower element heats both layers iff their temperatures are equal.
 * Do not understand the relationship between _Lused_ and the temperatures.

### Control and outcomes

 * 10,000 member population controlled.
 * For comfort, only the lower heating element was subjected to external control.
 * Two switches allowed the lower controller to be turned off completely, or
   subjected to a different thermostat.
 * Controller receives info on the states of all the water heaters' switches,
   and computes the amount of power it is able to increase or decrease demand by.
 * 5 minute hysterisis is explicitly included to ameliorate ocsillation.
 * Calculates the number of switches to change to achieve the desired increase/
   decrease in load.
 * Compared with no regulation, double the number of switches and 75% increase
   in number of discomforted users.
