#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame, sys, os.path
from pygame.locals import *
from retrogamelib import font
from retrogamelib.constants import NES_FONT
from random import randint, shuffle

class LayersStack:
    "Represents stack of backgrounds from top to bottom"
    def __init__(self, screen, layers, dy=0):
        self.layers=layers
        self.screen=screen
        self.screen_dim=screen.get_size()
        self.dy=dy

    def paint(self, speed):
        dy=self.dy
        
        for layer in self.layers:
            current_speed=int((dy+layer.height-self.dy)*speed/(self.screen_dim[1]-self.dy))
            screen.blit(layer.scroll(self.screen_dim[0],
                                     layer.speed is not None and layer.speed or current_speed), (0, dy),)
            dy+=layer.height

            
class Layer:
    def __init__(self, img, height=0, speed=None):
        self.img_filename=img
        self.img_surf=pygame.image.load(os.path.join('bike_data', self.img_filename)).convert_alpha()
        self.img_dim=self.img_surf.get_size()
        self.height= height!=0 and height or self.img_dim[1]
        self.speed=speed
        self.dx=0

    def scroll(self, screen_width, dx=0):
        dx+=self.dx
        self.dx= dx>=self.img_dim[0] and dx-self.img_dim[0] or dx

        self.surface=pygame.Surface((screen_width, self.img_dim[1]))
        self.surface.fill((2,2,2))
        self.surface.set_colorkey((2,2,2))
        self.surface.blit(self.img_surf,(0,0), (self.img_dim[0]-self.dx,0)+self.img_dim)

        dx=self.dx
        while dx<screen_width:
            self.surface.blit(self.img_surf, (dx,0))
            dx+=self.img_dim[0]

        return self.surface

class Rider:
    def __init__(self,img, frames, anims):
        self.img_filename=img
        self.img_surf=pygame.image.load(os.path.join('bike_data', self.img_filename)).convert_alpha()
        self.img_dim=self.img_surf.get_size()

        self.sprite_width=self.img_dim[0]/frames
        self.sprite_height=self.img_dim[1]/anims
        self.frames = range(0,self.img_dim[0], self.sprite_width)
        self.anims = range(0,self.img_dim[1], self.sprite_height)
        self.curr_frame=0
        self.curr_anim=0

    def show(self, anim=0,frame=0):
        return (self.frames[frame], self.anims[anim], self.sprite_width, self.sprite_height)
        
    def cycle(self, anim=0):
        self.curr_frame+=1
        self.curr_anim=anim
        if anim and anim!=self.curr_anim or self.curr_frame>=len(self.frames):
            self.curr_frame=0

        return (self.frames[self.curr_frame], self.anims[self.curr_anim],
                self.sprite_width, self.sprite_height)

#serial_port = serial.Serial('/dev/ttyUSB2', 9600, timeout=1)
    
pygame.init()
SCREEN=(640,480)
screen=pygame.display.set_mode(SCREEN)
clock=pygame.time.Clock()
    
layers= [ Layer('back.png', height=50), Layer('sidewalklamppost.png'),
          Layer('roadback.png', height=30), Layer('roadmiddle.png'), Layer('roadfront.png') ]
world=LayersStack(screen, layers)
player1=Rider('binky.png', 8,2)

# bike_data/m07.TTF
# bike_data/m08.TTF
# bike_data/m10.TTF
# bike_data/m17.TTF
# bike_data/m21.TTF
# bike_data/m22.TTF
# bike_data/m24.TTF
# bike_data/m26.TTF

font=pygame.font.Font('bike_data/m08.TTF', 60)  
#screen.blit(font.render("3, 2, 1... go", False, (255,255,255)), (20,440))

player_x=5
c=0

def intro(text="", time=500):
    global world, screen, font, player1
    
    world.paint(0)
    screen.blit(player1.img_surf, (player_x,240), player1.show())
    if text:
        screen.blit(font.render(text, False, (randint(0,255),randint(0,255),randint(0,255))),
                    (screen.get_width()/2, screen.get_height()/3))
    pygame.display.update()
    pygame.time.wait(time)

def read_input_file(fname):
    lines=open(fname).readlines()
    players=[]
    races=[]
    for l in lines:
        new_players=l.split()
        players+=new_players
        if len(new_players)==2: races.append(new_players)
        else: players_without_race+=new_players

    shuffle(players_without_race)
    races+=zip(players_without_race[::2], players_without_race[1::2])
    if len(players_without_race)%2==1: races.append([players_without_race[-1], ''])

    return races

try:
    pygame.draw.lines(screen, (255,255,255), True, [(20, 450), (620, 450), (620, 470), (20, 470)])
    intro("3\n1p313", 1000)
    intro()
    intro("2", 1000)
    intro()
    intro("1", 1000)
    intro()
    txt_surf=font.render("GO", False, (randint(0,255),randint(0,255),randint(0,255)))
    while c<280:
        if player_x<250 or c>200:
            world.paint(0)
            if c%5==0 and player_x<250:
                scale_factor=1+player_x/200.
                txt_surf2=pygame.transform.scale(txt_surf, (txt_surf.get_width()*scale_factor,
                                                            txt_surf.get_height()*scale_factor))
                screen.blit(txt_surf2,
                            (screen.get_width()/2-txt_surf2.get_width()/2, screen.get_height()/3))

                player_x+=6
        else:
            world.paint(-11)

        screen.blit(player1.img_surf, (player_x,240), player1.cycle())
        c+=1
        screen.fill((255,255,0), (22, 452, c*2, 16))
        clock.tick(20)
        pygame.display.update()

    screen_array = pygame.PixelArray(screen.copy())
    for y in range(44):
        for x in range(64):
            step=randint(1,5)
            color=(randint(0,255),randint(0,255),randint(0,255))
            for i in range(x*10,(x+1)*10):
                for j in range(y*10,(y+step)*10):
                    screen_array[i][j]=color

        screen.blit(screen_array.make_surface(), (0,y*10), (0,y*10,640,50))
        pygame.display.update((0,y*10,640,50))
        clock.tick(50)

except KeyboardInterrupt: sys.exit()


