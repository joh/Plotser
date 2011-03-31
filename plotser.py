#!/usr/bin/env python
#
# Plotser: real-time plotting of serial data
#
# See README for details
#
from collections import defaultdict
from itertools import cycle, chain
import serial
import gobject
import matplotlib
matplotlib.use('GTKAgg') # do this before importing pylab
from pylab import figure, show, draw, arange, sin

class PlotSer(object):

    # Available colors
    colors = cycle(('#990000', '#009900', '#000099'))
    
    def __init__(self, dev, baud=9600, window=2000):
        self.dev = dev
        self.baud = baud
        self.window = window
        
        self.ser = None
        
        self.time = 0
        self.X = []
        self.data = defaultdict(lambda: defaultdict(lambda: 0))
        self.lines = defaultdict(self.make_line)
        
        self.dmin = 0
        self.dmax = 1
    
    def make_line(self):
        line, = self.ax.plot([], [], self.colors.next())
        
        return line
    
    def read(self):
        """ Read a line from serial device """
        line = self.ser.readline().strip()
        
        print line
        
        try:
            data = map(int, line.split())
        except ValueError:
            return True
        
        self.X.append(self.time)
        
        for (i, d) in enumerate(data):
            self.data[i][self.time] = d
            
            self.dmin = min(self.dmin, d)
            self.dmax = max(self.dmax, d)
        
        if len(self.X) > self.window:
            t = self.X.pop(0)
            
            for d in self.data.values():
                d.pop(t, None)
        
        self.time += 1
        
        return True
    
    def update(self):
        if not self.X:
            return True
        
        for (i, d) in self.data.items():
            self.lines[i].set_data(self.X, [d[t] for t in self.X])
        
        self.ax.set_xlim(self.X[0], self.X[-1] + self.window / 4)
        self.ax.set_ylim(self.dmin, self.dmax)
        
        draw()
        
        return True
    
    def start(self):
        # Open serial device
        self.ser = serial.Serial(args.device, args.baudrate, timeout=5)
        self.ser.open()
        
        # Create figure & subplot
        self.fig = figure()
        self.fig.canvas.set_window_title('plotser: %s' % self.dev)
        
        self.ax = self.fig.add_subplot(111, autoscale_on=False, xlabel='time')
        
        gobject.idle_add(self.read)
        gobject.timeout_add(100, self.update)

        show()
        self.ser.close()




if __name__ == '__main__':
    # Parse command-line arguments
    import argparse
    
    parser = argparse.ArgumentParser(
        usage='%(prog)s [OPTION]... <device>',
        description='Real-time plotting of serial data')

    parser.add_argument('device', help='serial device to plot')
    parser.add_argument('-b', '--baudrate', type=int, default=9600, metavar='BAUD',
        help='serial baud rate (default: %(default)s)')

    args = parser.parse_args()
    
    g = PlotSer(args.device, args.baudrate)
    g.start()

