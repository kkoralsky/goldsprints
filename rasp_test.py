#!/usr/bin/python

from goldsprints import Output
import pygame

distance=400
unit=5
#roller_circum=.00025 # in meters
#dev='' # '02:11:09:20:01:96,00:11:11:29:06:20' 

out = Output((640,480), distance, unit, remote_vis='game', net='arasp:9998', fullscreen=True)

#gs=Goldsprints(out, dev=dev, dist=distance, unit=unit, roller_circum=roller_circum)

pygame.init()

out.new_race(('afda', 'fddd'))
out.start(('afda', 'fddd'))

pos=0
while pos<distance:
    pygame.time.wait(90)
    out.update_race(0, pos)
    pos+=1

out.finish
