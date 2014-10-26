from datetime import datetime

def to(results, model, dt, loadT, N, NC, NX, P):
    def report(t, T, u):
        if t - report.lastTime >= 3600:
            report.lastTime = t
            now = datetime.now()
            print '{}\t{:.2f}'.format(int(t/3600.0), (now - report.lastWallTime).total_seconds())
            report.lastWallTime = now
        if loadT(t)[0] > 0:
            if T[N-1] >= 50:
                results['satisfied'] += dt
            else:
                results['unsatisfied'] += dt
        if u[0] > 0:
            results['energy'] += u[0] * P * dt / 3.6e6
        [m_aux, U_aux, m_coll, m_coll_return] = model.lastInternalControl
        results['solar'] += m_coll * T[N+NC-1]
        results['auxiliary'] += m_aux * T[N+NC+NX-1]
    report.lastTime = 0
    report.lastWallTime = datetime.now()
    return report
 
def write(fname, results, verbose):
    with open(fname, 'w') as f:
        satisfaction = 100 if results['unsatisfied'] is 0 else \
            (results['satisfied'] / float(results['satisfied'] + results['unsatisfied']) * 100)
        fraction = 100 if results['auxiliary'] is 0 else \
            (results['solar'] / float(results['solar'] + results['auxiliary']) * 100)
        energy = results['energy']

        if verbose:
            f.write('Satisfaction: {:.2f}%\n'.format(satisfaction))
            f.write('Energy used: {:.2f}kWh\n'.format(energy))
            f.write('Solar fraction: {:.2f}%\n'.format(fraction))
        else:
            f.write('{:.2f}\t{:.2f}\t{:.2f}'.format(satisfaction, energy, fraction))
