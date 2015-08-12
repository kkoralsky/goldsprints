#-*- coding: utf-8 -*-

from goldsprints import Race, Goldsprints

import pygame, pygame.font, pygame.event, pygame.draw, string, sys
from pygame.locals import *
from threading import Thread

class PgFront(Thread):
  daemon=True
  
  def __init__(self, gs, primary_vis):
      Thread.__init__(self)
      
      self.name="PgFront"
      self.gs=gs
      self.vis=primary_vis
      pygame.key.set_repeat(200,100)
      

  def ask_for_names(self):
    self.gs.race_is_runing=True # lock other means of starting new race

    self.vis.show_inputs()
    self.vis.switch_virt_keyboard()
#    self.vis.show_sets(self.gs.sets)

    focus=0
    names=["",""]
    set_pos=[0,0]
    r=None

    while 1:
      ev=pygame.event.wait()
      if ev.type==USEREVENT+1:
        self.vis.anim_cursor(focus, len(names[focus]))
      elif ev.type==USEREVENT and ev.code==1:
        self.vis.go_next=True
      elif ev.type==KEYDOWN:
        if ev.key==K_RETURN or ev.key==270:
          rset=[ self.gs.sets[p] for p in set_pos ]
          return [ p['name'] and p or None
                   for p in map(dict, zip(zip(['name']*2, names), zip(['set']*2, rset))) ]
        elif ev.key==K_ESCAPE:
          return [None,None]
        elif ev.key==K_TAB or ev.key==269:
          focus=int(not focus)
          self.vis.curr_keycode=0
          self.vis.switch_virt_keyboard(focus)
          self.vis.anim_cursor(focus, len(names[focus]), show=True)
        elif ev.key==K_LEFT or ev.key==260:
          self.vis.switch_virt_keyboard(focus, self.vis.key_PREV)
        elif ev.key==K_RIGHT or ev.key==265:
          self.vis.switch_virt_keyboard(focus, self.vis.key_NEXT)
        elif ev.key==K_UP or ev.key==262:
          self.vis.switch_virt_keyboard(focus, self.vis.key_UP)
        elif ev.key==K_DOWN or ev.key==263:
          self.vis.switch_virt_keyboard(focus, self.vis.key_DOWN)
#         elif ev.key==K_LEFT or ev.key==K_RIGHT:
#           if ev.key==K_LEFT and set_pos[focus]>0: set_pos[focus]-=1
#           elif ev.key==K_RIGHT and set_pos[focus]<len(self.gs.sets)-1: set_pos[focus]+=1
#           self.vis.show_sets(self.gs.sets, focus, set_pos[focus])
        else:
          if (ev.key==K_BACKSPACE or ev.key==258) and len(names[focus])>0:
            names[focus]=names[focus][:-1]
          elif ev.key in (K_LCTRL, K_RCTRL, 257) and len(names[focus])<15:
            names[focus]+=chr(self.vis.keycodes[self.vis.curr_keycode])
          elif (ev.key==K_SPACE or (ev.key>=97 and ev.key<=122)) and len(names[focus])<15:
            names[focus]+=chr(ev.key)
          self.vis.print_names(focus, names[focus])
          self.vis.anim_cursor(focus, len(names[focus]), show=True)

  def run(self):
      #self.vis.welcome()
      r=None
      while not self.gs.quit.is_set():
          ev=pygame.event.wait()
          if ev.type==QUIT:
              self.gs.abort.set()
              self.gs.quit.set()
              if self.gs.another_vis:
                self.gs.another_vis.kill()
              sys.exit()
          if ev.type==KEYDOWN:
              if ev.key==K_RETURN or ev.key==270: # [+]
                if self.gs.race is None:
                  players=self.ask_for_names()
                  if any(players): Race(self.gs, players, 'none')
                  self.vis.repaint_dist_widg()
                elif not self.gs.race_is_runing:
                  self.gs.race.start()
              elif ev.key==K_f: pygame.display.toggle_fullscreen()
              elif ev.key==K_q or ev.key==K_ESCAPE or ev.key==K_a or ev.key==269:
                if self.gs.race_is_runing:
                  self.gs.abort.set()
                if ev.key==K_q:
                  self.gs.quit.set()
                  sys.exit()
              elif self.gs.race and not self.gs.race_is_runing:
                if (ev.key==K_LEFT or ev.key==260) and self.gs.dist>10:
                  self.gs.dist-=10
                elif (ev.key==K_RIGHT or ev.key==265) and self.gs.dist<10000:
                  self.gs.dist+=10
                elif (ev.key==K_UP or ev.key==262) and self.gs.dist<10000:
                  self.gs.dist+=100
                elif (ev.key==K_DOWN or ev.key==263) and self.gs.dist>100:
                  self.gs.dist-=100
                  
                self.gs.out.set_dist(self.gs.dist)                  
                self.vis.repaint_dist_widg()

if __name__ == "__main__":
  from visualize import ClientVis
  
  PgFront(Goldsprints(ClientVis((640,480)), None, 100, 5, 0, sets=['male', 'female'])).run()
