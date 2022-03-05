import time
import sys


class debugtime(object):
    """debugtimer returns a Timer object that can be used
    to time the running of portions of code, and then
    write a simple report of the results.  the Timer object
    has methods:

      clear()                  reset Timer
      add(msg, verbose=False)  record time, with message
      get_report()             get text of timer report
      show()                   print timer report

    An example:

      timer = debugtimer()
      x = 1
      timer.add('now run foo')
      foo()
      timer.add('now run bar')
      bar()
      timer.show_report()
    """
    def __init__(self):
        self.clear()
        self.add('debugtime init')

    def clear(self):
        self.times = []

    def add(self,msg='', verbose=False):
        # print msg
        self.times.append((msg,time.time()))
        if verbose:
            sys.stdout.write("%s\n"% msg)

    def show(self, writer=None, clear=True):
        if writer is None:
            writer = sys.stdout.write
        writer('%s\n' % self.get_report())
        if clear:
            self.clear()


    def get_report(self):
        m0, t0 = self.times[0]
        tlast= t0
        out  = ["# %s  %s " % (m0,time.ctime(t0))]
        lmsg = 0
        for m, t in self.times[1:]:
            lmsg = max(lmsg, len(m))
        m = '#      Message'
        m = m + ' '*(lmsg-len(m))

        out.append("#--------------------" + '-'*lmsg)
        out.append('%s        Delta(s)     Total(s)' % (m))
        for m,t in self.times[1:]:
            tt = t-t0
            dt = t-tlast
            if len(m)<lmsg:
                m = m + ' '*(lmsg-len(m))
            out.append(" %s   %10.4f    %10.4f" % (m,dt, tt))
            tlast = t
        return '\n'.join(out)
