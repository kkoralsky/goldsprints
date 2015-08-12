#!/usr/bin/python

import argparse
import os
import random
import time
import serial

parser = argparse.ArgumentParser(prog='fakerace.py',
                                 description="run faked race of goldsprints")

parser.add_argument('pace', metavar='P', type=float,
                    help='number/fraction of seconds between each player move (race rate in other words)')
parser.add_argument('-d', '--dist', type=int, default=5,
                    help='''distance that each player has to beat until he finish;
                    if argument not specified or 0, then players will ride till infinity''')
parser.add_argument('--pace-entropy', type=float, nargs=2, default=[0,0],
                    metavar='PE',
                    help='''specify range of number/fraction of seconds that are added
                    or subtracted from P (pace) on each move''')
parser.add_argument('-v', '--players', default='10', type=str,
                    metavar='PLAYERS',
                    help='''character string that defines number of players (length of the string)
                    and characters that corresponds each player move''')
parser.add_argument('-f', '--file', default='fake.in', type=str,
                    help='''file to which record race (same file has to be given
                    as argument for goldsprints app)''')

args = parser.parse_args()

random.seed()
cur_dist = dict.fromkeys(args.players, 0)
#f = open(args.file, 'a', buffering=0)
ser = serial.Serial(args.file)

def race_ended(cur_dist, dist):
    if dist==0:
        return True
    else:
        return all([d==dist for d in cur_dist.values()])


while not race_ended(cur_dist, args.dist):
    cur_player = random.choice(args.players)
    #f.write(cur_player)
    ser.write(cur_player)
    cur_dist[cur_player]+=1
    cur_pace = random.uniform(args.pace_entropy[0], args.pace_entropy[1])
    if random.choice([True, False]):
        cur_pace=-cur_pace
    time.sleep(abs(args.pace+cur_pace))

#f.close()
ser.close()
