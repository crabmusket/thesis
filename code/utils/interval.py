class Interval(object):
    def __init__(self, f=None):
        self.intervals = []
        self.fn = f

    def const_for(self, v, t=0):
        v0 = self.fn(v) if self.fn is not None else v
        tf = t
        if len(self.intervals) > 0:
            tf = t + self.intervals[-1][0]
        self.intervals.append((tf, v0))
        return self

    def const_til(self, v, t):
        v0 = self.fn(v) if self.fn is not None else v
        self.intervals.append((t, v0))
        return self

    def __call__(self, t):
        for i in self.intervals:
            if t <= i[0]:
                return i[1]
        return self.intervals[-1][1]
