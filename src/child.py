#!/usr/bin/python
#encoding:utf8

from visualize import BarVis, GameVis
import sys, pygame

vis=eval(sys.argv[1])

    #BarVis((640, 480), *(map(int, sys.argv[1:])+['secondary']))

try:
    while 1:
        input()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                sys.exit()
except KeyboardInterrupt:
    sys.exit()
