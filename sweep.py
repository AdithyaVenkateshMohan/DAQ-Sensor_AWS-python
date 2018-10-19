from sweeppy import app
import threading
import pandas
import numpy


def scan(duration):
    dev = '/dev/ttyUSB0'
    done = threading.Event()
    timer = threading.Timer(duration, lambda: done.set())
    fifo = app.queue.Queue()
    scanner = app.Scanner(dev, fifo, done)
    counter = app.SampleCounter(fifo)
    scanner.start()
    counter.start()
    timer.start()
    scans = counter.run()
    all_samples = app.process_scans(scans)
    all_samples = pandas.DataFrame(all_samples)
    all_samples.columns = ['degrees','distance', 'strength']
    all_samples['degrees'] = all_samples['degrees'] / 1000 # milli-degress to degrees
    all_samples['rad'] = numpy.deg2rad(all_samples['degrees'])
    all_samples['distance'] = all_samples['distance'] / 10 # cm to mm
    all_samples['x'] = all_samples['distance'] * numpy.cos(all_samples['rad'] )
    all_samples['y'] = all_samples['distance'] * numpy.sin(all_samples['rad'])
    print('scan done')
    return all_samples


#raw = scan(5)
#raw = raw[raw['strength'] > 50]
#raw['round'] = numpy.round(raw['degrees'])

#mns = raw.groupby('degrees')
#mns = mns.mean()
#mns = mns.reset_index()

#pyplot.plot(mns['x'],mns['y'],'.')
#pyplot.show()

