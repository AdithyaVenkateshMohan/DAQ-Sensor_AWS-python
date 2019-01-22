from sweeppy import Sweep
print('enga va ya')

with Sweep('/dev/ttyUSB0') as sweep:
    sweep.start_scanning()

    print 'hello'

    for scan in sweep.get_scans():
        print('{}\n'.format(scan))