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
            results['energy'] += u[0] * P * dt
        [m_aux, U_aux, m_coll, m_coll_return] = model.lastInternalControl
        results['solar'] += m_coll * T[N+NC-1]
        results['auxiliary'] += m_aux * T[N+NC+NX-1]
    report.lastTime = 0
    report.lastWallTime = datetime.now()
    return report
 
def write(fname, results):
    with open(fname, 'w') as f:
        if results['unsatisfied'] is 0:
            f.write('Satisfaction: {:.2f}%\n'.format(100))
        else:
            f.write('Satisfaction: {:.2f}%\n'.format(
                results['satisfied'] / float(results['satisfied'] + results['unsatisfied']) * 100
            ))
        f.write('Energy used: {:.2f}kWh\n'.format(
            results['energy'] / (3.6e6)
        ))
        if results['auxiliary'] is 0:
            f.write('Solar fraction: {:.2f}%\n'.format(100))
        else:
            f.write('Solar fraction: {:.2f}%\n'.format(
                results['solar'] / float(results['solar'] + results['auxiliary']) * 100
            ))
