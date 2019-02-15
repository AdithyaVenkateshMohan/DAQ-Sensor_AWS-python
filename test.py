from sweeppy import Sweep
print('enga va ya')

with Sweep('/dev/ttyUSB0') as sweep:
    sweep.start_scanning()

    print 'hello'

    for scan in sweep.get_scans():
        print('bx = fig.add_subplot(111){}\n'.format(scan))