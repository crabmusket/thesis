def setup(parser):
    parser.add_argument('--month',   default=6, type=int,
        help='Which month to start the simulation in.')
    parser.add_argument('--day',   default=1, type=int,
        help='Which day of the month to start the simulation on.')

    parser.add_argument('--days',    default=8, type=int,
        help='Number of days the sinulation will run for.')
    parser.add_argument('--start',   type=int,
        help='Start graphing at the start of this day (indexed from 0).')
    parser.add_argument('--end',     type=int,
        help='End graphing at the end of this day (indexed from 0).')

    parser.add_argument('--width',   default=6, type=float,
        help='Width in inches of the resulting plot')
    parser.add_argument('--height',  default=4, type=float,
        help='height in inches of the resulting plot.')

    parser.add_argument('--setpoint', default=60, type=int,
        help='Setpoint for internal tank thermostats.')
    parser.add_argument('--deadband', default=5,  type=int,
        help='Deadband for internal control thermostats.')
    parser.add_argument('--cset', default=8, type=int,
        help='Setpoint for differential collector thermostat.')
    parser.add_argument('--cdead', default=6, type=int,
        help='Deadband for differential collector thermostat.')

    parser.add_argument('--cost',    default=1, type=float,
        help='Weight on the input term of the cost function.')
    parser.add_argument('--horizon', default=6, type=int,
        help='Number of hours to predict into the future.')

    parser.add_argument('--loadP',         default='data/daily_load.txt',
        help='File containing load prediction values.')
    parser.add_argument('--insolationP',   default='data/insolation.txt',
        help='File containing insolation prediction values.')
    parser.add_argument('--ambientP',      default='data/ambient.txt',
        help='File containing ambient prediction values.')

    parser.add_argument('--internals',     action='store_true',
        help='Show controller\'s prediction of average temperature at each timestep.')
    parser.add_argument('--alltemps',      action='store_true',
        help='Show all tank temperatures, instead of just the top and bottom.')
    parser.add_argument('--verbose', default=False, type=bool,
        help='Print results to file in a verbose fashion')

    parser.add_argument('name',
        help='Filename prefix for plot and results.')
