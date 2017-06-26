#!/usr/bin/env python

import os
import re
import csv
import sys
from optparse import OptionParser
from pickle import load, UnpicklingError
from subprocess import Popen, PIPE
import site
site.addsitedir('src')

from cmdserver import CommandServer
from pgfrontend import PgFront
from goldsprints import Goldsprints, CMWCGoldsprints, Output
from qtcontrol import QtControl, OutInterface
from device import BluetoothDev, SerialDev, Dev, DoubleSerialDev, RaspGPIODev, ShmReader, PygameDev


screen_res=(640,480)

distance=400
unit=5
roller_circum=.00025 # in km
dev=''
output_file='results.txt'
input_file='input.txt'
false_start=5
sampling = 0.04

p = OptionParser(conflict_handler="resolve", version="%prog 0.8",
                 usage="%prog [options] [<input_times>]",
                 description="GOLDSPRINTS")
p.add_option('--version', '-v', action='version', help='print version of program')
p.add_option('--distance', '-d', action='store', type='int', default=distance)
p.add_option('--unit', '-u', action='store', type='int', default=unit)
p.add_option('--roller_circum', '-r', action='store', type='float', default=roller_circum)

p.add_option('--sampling', '-m', action='store', type='float', default=sampling,
             help="time period every which vis. frame is painted")
p.add_option('--dev', '-s', action='store', type='str', default=dev,
             help="""specify device counting roller turns; could be a pair of bluetooth MACs (xx:xx:xx:xx:xx:xx,xx:xx:xx:xx:xx:xx)
             or serial device name (like /dev/ttyUSB0 or COM38) if not specified, assuming test mode""")
p.add_option('--threshold', '-t', action='store', type=int, default=5,
             help="number of signals that trigger 1 player move; default=5")
p.add_option('--output', '-o', action='store', type='str', default=output_file)
p.add_option('--finals_output', action='store', type='str', default='finals.pickle')

p.add_option('--false-start', '-e', action='store', type='int', default=false_start)
p.add_option('--fullscreen', '-f', action='store_true', default=False)
p.add_option('--local', '-l', action='store', type='str', default='',
             help='local visualization(s) game and/or bar (comma seperated)')
p.add_option('--remote', '-r', action='store', type='str', default='bar',
             help='remote visualization(s) game and/or bar (comma seperated; bar by default)')
p.add_option('--network', '-n', action='store', type='str', default='',
             help='send visualization data over network')
p.add_option('--kiosk', '-k', action='store_true', default=False, help='do not open control window but use pygame frontend')
p.add_option('--headless', '-c', action='store_true', default=False,
             help='run headless')
#p.add_option('--cmwc', '-c', action='store', type='str', default='',
             #metavar='CSV_FILE', help='starts CMWC goldsprints and loads csv file of participants')
p.add_option('--recover_finals', action='store', type='str', default=None)
p.add_option('--sets',  action='store', type='str', default='_',
             help='comma seperated (no spaces between) sets of competition; for ex.: male,female')
p.add_option('--welcome', '-w', action='store_true', default=False)

opts, args = p.parse_args()

out=Output(screen_res, opts.distance, opts.unit, opts.local, opts.remote,
           opts.fullscreen, opts.network, opts.output, opts.finals_output,
           OutInterface())

#out.primary_vis.welcome()

try:
    if opts.dev.startswith('D:'):
        if opts.dev.startswith('D:SHMEM'):
            dev = ShmReader(opts.dev[len('D:SHMEM:'):], opts.threshold,
                            opts.false_start)
        else:
            dev = SerialReader(opts.dev[len('D:'):], opts.threshold)
    elif opts.dev.find(',')>0:
        if opts.dev.find(':')>0:
            dev=DoubleBluetoothDev(opts.dev, opts.threshold)
        elif re.match(r'\d{1,2}[UD],\d{1,2}[UD]', opts.dev):
            dev = RaspGPIODev(opts.dev, opts.threshold)
        else:
            dev = DoubleSerialDev(opts.dev, opts.threshold)
    else:
        if opts.dev.find(':')>0:
            dev=BluetoothDev(opts.dev, opts.threshold)
        elif os.path.exists(opts.dev):
            dev=SerialDev(opts.dev, opts.threshold)
        else:
            dev = PygameDev()
except ValueError:
    print('ERROR while initializing device')
    dev=Dev(threshold=opts.threshold)
except ImportError, e:
    print('ERROR while import proper module')
    print(e)

gs=Goldsprints(out, dev, opts.distance, opts.unit, opts.sampling,
               opts.roller_circum, sets=opts.sets.split(','))


if args and len(args)==1 and os.path.exists(args[0]):
    for r in csv.reader(open(args[0])):
        r=[ float(r[0]), dict(zip(('set', 'name'), r[1:])) ]
        if r[1]['set'] in gs.sets:
            gs.times[r[1]['set']].append(r)

    for s in gs.sets:
        gs.best_times[s]=gs._gen_bt(s)

if opts.recover_finals is not None:
    for s in gs.sets: gs.best_times[s]=gs._gen_bt(s)
    try:
        finals=load(open(opts.recover_finals))
        for a,f in finals: setattr(gs, a, f)
    except IOError: print('openning file, failed')
    except UnpicklingError, e: print('unpickling error: {0}'.format(e))
    except AttributeError, e: print('not {0} in gs instance ({1})'.format(a, e))
    finally: sys.exit()

# if not opts.network:
#     PgFront(gs, out.primary_vis).start()

if opts.headless:
    CommandServer(gs, daemon=True).run()
else:
    CommandServer(gs, daemon=True).start()

    if opts.kiosk:
        PgFront(gs, out.primary_vis).run()
    else:
        QtControl(gs).run()
