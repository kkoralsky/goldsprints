#!/usr/bin/python
#encoding:utf8

from goldsprints import Output
import pygame
import sys
import socket
from time import sleep

class RemoteChild:
    out=None

    def __init__(self,port):
        self.s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('', int(port)))
        self.s.settimeout(1)

    def new_main(self,res,dist,unit,vis,fullscreen):
        if self.out is None:
            self.out=Output(res,dist,unit,vis,'',fullscreen)
        else:
            if vis.split(',')!=self.out.vis or fullscreen!=self.out.fullscreen or res!=self.out.res:
                self.out.quit()
                self.out=Output(res,dist,unit,vis,'',fullscreen)
            else:
                if dist!=self.out.dist:
                    self.out.set_dist(dist)
                elif unit!=self.out.unit:
                    self.out.set_unit(unit)

    def run(self):
        while 1:
            #if self.out:
                #for ev in pygame.event.get():
                    #if ev.type == pygame.QUIT:
                        #sys.exit()
                #pygame.display.update()
            try:
                command, addr = self.s.recvfrom(1000)
                if command == '__try':
                    self.s.sendto('__catch', addr)
                    continue
                try:
                    print(command)
                    exec('self.'+command.strip())
                except Exception, e:
                    print '!! ', e
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                self.out.quit()
                self.s.shutdown()
                del self.out
                sys.exit()


if __name__=="__main__":
    remote_child=RemoteChild(sys.argv[1])
    remote_child.run()
