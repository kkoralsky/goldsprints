#!/usr/bin/python

port=9999

import pygame
from pygame.locals import *

from visualize import CMWCClientVis
from goldsprints import CMWCGoldsprints as GS

from glob import glob
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
import sys

players=GS.load_participants(open(glob('cmwc2011_participants*.csv')[-1]))

def check_pl(number):
    global players
    if len(number)>0:
        number=int(number)
        if number<1000 and isinstance(players[number], dict):
            return players[number]

def clear():
    global focus, racers, confirmed, race_numbers, vis, sent

    focus=0
    racers=[None,None]
    confirmed=[False,False]
    race_numbers=['','']

    vis._transition()
    vis.screen.fill((0,0,0))
    vis._center('type your racenumber and', font=vis.head_font, y=20, color=(50,)*3)
    vis._center('confirm by pressing Enter', font=vis.head_font, y=50, color=(50,)*3)
    vis.show_inputs()
    vis.anim_cursor(0)
    sent=False

if __name__ == "__main__":
    vis=CMWCClientVis((640, 480), fullscreen=len(sys.argv)==3, title='CMWC 2011 GOLDSPRINTS      WWA')

#     vis.show_inputs()

    s=socket(AF_INET, SOCK_STREAM)
    s.connect((sys.argv[1], port))

    clear()

    next_race=5
    while 1:
        for ev in pygame.event.get():
            if ev.type==USEREVENT+1:
                if all(confirmed):
                    next_race+=1
                    if next_race==5:clear()
                else:
                    vis.anim_cursor(focus, len(race_numbers[focus]))
            elif ev.type==KEYDOWN:
                if ev.key==K_ESCAPE:
                    #s.shutdown(SHUT_RDWR)
                    s.close()
                    sys.exit()
                elif ev.key in (K_RETURN, K_KP_ENTER):
                    if sent:
                        clear()
                    elif all(confirmed):
                        if any(racers) and race_numbers[0]!=race_numbers[1]:
                            s.send('cmwc_add_race({0}, {1})\n'.format(*[r and r['__race_number']
                                                                          for r in racers]))
                            vis.screen.fill((0,0,0), (200, 440, 300, 100))
                            vis.write_down('              ', 440)
                            resp=s.recv(256)
                            if resp=='added.\r\n':
                                vis.new_race([r and r['name'] for r in racers])
                                next_race=0
                            else: vis.show(resp)
                            sent=True
                        else: clear()
                    else:
                        racers[focus]=check_pl(race_numbers[focus])
                        confirmed[focus]=True
                        if racers[focus]:
                            vis.show_player(focus, racers[focus])
                        else:
                            vis.show_player(focus, msg='nothing.')

                        focus=int(not focus)
                        if all(confirmed) and any(racers) and race_numbers[0]!=race_numbers[1]:
                            vis.write_down('press enter', 440)

                elif ev.key==K_TAB:
                    focus=int(not focus)
                    vis.anim_cursor(focus, len(race_numbers[focus]), show=True)
                elif ev.key==K_BACKSPACE:
                    if all(confirmed):
                        clear()
                    elif confirmed[focus]:
                        confirmed[focus]=False
                        race_numbers[focus]=''
                        vis.show_inputs(focus)
                        vis.show_player(focus)
                        vis.anim_cursor(focus, show=True)
                    else:
                        race_numbers[focus]=race_numbers[focus][:-1]
                        vis.print_racenumber(focus,race_numbers[focus])
#                 elif ev.key==K_l:
#                     players=GS.load_participants(open(glob('cmwc2011_participants*.csv')[-1]))
                elif len(race_numbers[focus])<=2 and not all(confirmed) and \
                     ((ev.key>=K_KP0 and ev.key<=K_KP9) or (ev.key>=K_0 and ev.key<=K_9)):
                    key_num=ev.key
                    if ev.key>=K_KP0:
                        key_num-=208
                    race_numbers[focus]+=chr(key_num)
                    vis.print_racenumber(focus, race_numbers[focus])
                    vis.anim_cursor(focus, len(race_numbers[focus]), show=True)
                    
