# -*- coding: utf-8 -*-

import pygame
import os.path
from threading import Thread, Event

from random import randint, shuffle
from time import sleep
from copy import copy

BASE_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')

class LayersStack:
    "Represents stack of backgrounds from top to bottom"
    def __init__(self, screen, layers, dy=0):
        self.layers=layers
        self.screen=screen
        self.screen_dim=screen.get_size()
        self.dy=dy

    def paint(self, speed=0):
        dy=self.dy

        for layer in self.layers:
            current_speed=int((dy+layer.height-self.dy)*speed/(self.screen_dim[1]-self.dy))
            self.screen.blit(layer.scroll(self.screen_dim[0],
                                          layer.speed is not None and layer.speed or current_speed),
                             (0, dy))
            dy+=layer.height


class Background:
    def __init__(self, screen, img):
        self.dx = 0
        self.screen = screen
        self.screen_dim = self.screen.get_size()
        self.surf = pygame.image.load(os.path.join(BASE_DATA_PATH, img)).convert_alpha()
        self.dim = self.surf.get_size()

    def paint(self, speed=0):
        self.dx-=speed
        if self.dx >= self.dim[0]:
            self.dx = 0
        self.screen.blit(self.surf, (0,0), (self.dx,0)+self.screen_dim)
        if self.dx > self.dim[0]-self.screen_dim[0]:
            to_fill = self.dim[0]-self.dx
            self.screen.blit(self.surf, (to_fill, 0),
                             (0, 0, self.screen_dim[0]-to_fill, self.dim[1]))


class Layer:
    "Single background with colorkey set to (2,2,2)"
    def __init__(self, img, height=0, speed=None):
        self.img_filename=img
        self.img_surf=pygame.image.load(os.path.join(BASE_DATA_PATH, self.img_filename)).convert_alpha()
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
    "Represents rider sprite. has its actual position on the screen"
    def __init__(self,img, frames, anims, pos):
        self.img_filename=img
        self.img_surf=pygame.image.load(os.path.join(BASE_DATA_PATH, self.img_filename)).convert_alpha()
        self.img_dim=self.img_surf.get_size()

        self.sprite_width=self.img_dim[0]/frames
        self.sprite_height=self.img_dim[1]/anims
        self.frames = range(0,self.img_dim[0], self.sprite_width)
        self.anims = range(0,self.img_dim[1], self.sprite_height)
        self.curr_frame=0
        self.curr_anim=0

        self.pos=pos
        self.init_pos=pos # initial coordinates

    def reset(self):
        self.pos=copy(self.init_pos)

    def show(self, anim=0,frame=0):
        return (self.frames[frame], self.anims[anim], self.sprite_width, self.sprite_height)

    def cycle(self, anim=0):
        self.curr_frame+=1
        self.curr_anim=anim
        if anim and anim!=self.curr_anim or self.curr_frame>=len(self.frames):
            self.curr_frame=0

        return (self.frames[self.curr_frame], self.anims[self.curr_anim],
                self.sprite_width, self.sprite_height)


class AnimatedText:
    i=0
    def __init__(self, txt, font, colors=None, scale=0):
        self.font=font
        self.txt=txt
        if colors is not None: self.colors=colors
        self.scale=scale
        self.scale_factor=scale

        self.size=self.font.size(txt)
        self.txt_surf=self.font.render(self.txt, False, (255,)*3)
        self.txt_surf.set_colorkey((255,)*3)

    def get_size(self):
        if self.scale:
            return (self.size[0]+self.scale, self.size[1]+self.scale)
        else:
            return self.size


class ColoredText(AnimatedText):
    colors = [(140,190,65), (255, 221, 19), (35,31,32), (237,28,36), (14,118,188)]

    def anim(self, first=0):
        if first: self.i=first

        render_surf=pygame.Surface(self.txt_surf.get_size())

        for i in range(len(self.colors)):
            k=self.i+i
            if k>=len(self.colors): k=k-len(self.colors)
            render_surf.fill(self.colors[k], (0,i*self.size[1]/len(self.colors),
                                              self.size[0], self.size[1]/len(self.colors)))

        render_surf.blit(self.txt_surf, (0,0))
        render_surf.set_colorkey((0,)*3)
        if self.scale:
            render_surf=pygame.transform.scale(render_surf,
                                               (render_surf.get_width()+self.scale,
                                                render_surf.get_height()+self.scale))
            self.scale+=self.scale_factor


        self.i+=1
        if self.i==len(self.colors): self.i=0

        return render_surf


class GradientText(AnimatedText):
    def __init__(self, res, *args, **kwargs):
        AnimatedText.__init__(self, *args, **kwargs)

        w, h = self.txt_surf.get_size()
        self.gradient_surf = pygame.Surface((w,h))
        h/=2
        surf=self.gradient_surf.subsurface((0,0,w,h))

        rate = (float(self.colors[1][0]-self.colors[0][0])/h,
                float(self.colors[1][1]-self.colors[0][1])/h,
                float(self.colors[1][2]-self.colors[0][2])/h)

        for l in range(0, h+res, res):
            color = (min(max(self.colors[0][0]+(rate[0]*l),0),255),
                     min(max(self.colors[0][1]+(rate[1]*l),0),255),
                     min(max(self.colors[0][2]+(rate[2]*l),0),255))
            pygame.draw.line(surf, color, (0,l), (w,l), res)

        self.res=res
        self.gradient_surf.blit(pygame.transform.flip(surf, False, True), (0,h))

    def anim(self):
        render_surf=self.gradient_surf.copy()
        render_surf.scroll(0, self.i*self.res)
        render_surf.blit(self.gradient_surf, (0,0),
                         (0, self.size[1]-self.i*self.res, self.size[0], self.i*self.res))
        render_surf.blit(self.txt_surf, (0,0))
        render_surf.set_colorkey((0,)*3)
        self.i+=1
        if self.size[1]-self.i*self.res<=self.res: self.i=0
        return render_surf


class Visualize:
    "Base class for visualizing stuff"
    speed=[0,0]

    def __init__(self, resolution, dist=0, unit=None, fullscreen=False, title=''):
        #import pygame
        pygame.init()
        self.resolution=resolution
        self.dist=dist
        self.unit=unit
        self.screen = pygame.display.set_mode(resolution, fullscreen and pygame.FULLSCREEN or 0)

        self.go_ev=pygame.event.Event(pygame.USEREVENT, code=1)
        self.go_next=False
        self.abort=Event()

        pygame.mouse.set_visible(False) # hiding mouse cursor
        self.font=pygame.font.Font(os.path.join(BASE_DATA_PATH, 'm50.ttf'), 60)
        self.outline_font=pygame.font.Font(os.path.join(BASE_DATA_PATH, 'm50.ttf'), 70)
        self.head_font=pygame.font.Font(os.path.join(BASE_DATA_PATH, 'm50.ttf'), 25)
        self.huge_font=pygame.font.Font(os.path.join(BASE_DATA_PATH, 'm26.TTF'), 300)
        self.title=title
        if self.title:
            pygame.display.set_caption(self.title)
        else:
            pygame.display.set_caption('GOLDSPRINTS')


    def _transition(self):
        for y in range(44):
            for x in range(64):
                color=(randint(5,10),randint(5,10),randint(5,10))
                self.screen.fill(color, (x*10, y*10, 10,10))

        #self._center('WFK', font=self.huge_font, color=(0,0,0))

        self.screen.fill((0,)*3, (0,440, 640, 40))

        pygame.display.update()#(x*10,y*10,10,10))
        #pygame.time.wait(500)

    def _center(self, txt, y=None, color=(255,255,255), font=None, outline=0):
        if font is None:
            font=self.font
        txt_surf=font.render(txt, False, color)
        txt_size=txt_surf.get_size()
        if outline:
            outline_surf=pygame.Surface([d+outline for d in txt_size])
            outline_surf.fill((0,)*3)
            if y is None:
                y=self.resolution[1]/2-(txt_size[1]+outline)/2
            r1=self.screen.blit(outline_surf, (self.resolution[0]/2-(txt_size[0]+outline)/2, y))
            y+=outline/2
        else:
            if y is None: y=self.resolution[1]/2-txt_size[1]/2

        r2=self.screen.blit(txt_surf, (self.resolution[0]/2-txt_size[0]/2, y))
        if outline: return r1
        else: return r2

    def welcome(self):
        w=self.font.render('W', False, (255,100,0))
        f=self.font.render('F', False, (255,100,0))
        k=self.font.render('K', False, (255,100,0))

        pygame.display.update(self.screen.blit(w, (self.resolution[0]/2-f.get_width()/2-w.get_width(),
                                                   self.resolution[1]/8)))
        pygame.time.wait(200)
        pygame.display.update(self.screen.blit(f, (self.resolution[0]/2-f.get_width()/2,
                                                   self.resolution[1]/8)))
        pygame.time.wait(200)
        pygame.display.update(self.screen.blit(k, (self.resolution[0]/2+f.get_width()/2,
                                                   self.resolution[1]/8)))
        pygame.time.wait(200)
        pygame.display.update(self._center('studios', y=self.resolution[1]/8+f.get_height()-10,
                                           color=(255,100,0),
                                           font=pygame.font.Font(os.path.join(BASE_DATA_PATH, 'm08.TTF'), 30)))
        pygame.time.wait(1000)
        pygame.display.update(self._center('presents', self.resolution[1]/8+f.get_height()+30,
                                           color=(255,255,255), font=self.head_font))
        pygame.time.wait(1500)

        goldsprints = self.font.render('GOLDSPRINTS', False, (255,255,0))
        goldsprints_shadow = self.font.render('GOLDSPRINTS', False, (255,255,255))
        r1=r2=pygame.Rect(0,0,0,0)
        for i in range(6):
            pygame.time.wait(150)
            pygame.display.update(self.screen.fill((0,0,0),r1.union(r2)))

            pygame.time.wait(100)
            r1=self.screen.blit(goldsprints_shadow, (self.resolution[0]/2-goldsprints.get_width()/2+5,
                                                     self.resolution[1]/2+5))
            r2=self.screen.blit(goldsprints, (self.resolution[0]/2-goldsprints.get_width()/2,
                                              self.resolution[1]/2))

            pygame.display.update((r1,r2, self._center('WWA 2011', self.resolution[1]/2+r1.height+10,
                                                       font=self.head_font)))
        y=r2.bottom+40
        while y>0:
            buf=self.screen.copy()
            self.screen.fill((0,0,0))
            pygame.display.update(self.screen.blit(buf, (0,0), (0,10, 640, y)))
            pygame.time.wait(150)
            y-=10


    def new_race(self, players, type='regular'):
        self._transition()
        #pygame.display.update(self.screen.fill((0,0,0)))

        #if   type=='third_place': r=[self.screen.blit(ColoredText('third place', self.font).anim(3), (10, 10))]
        #elif type=='final':       r=[self.screen.blit(ColoredText('final race', self.font).anim(3), (40, 10))]
        #elif type=='finals':      r=[self.screen.blit(ColoredText('finals race', self.head_font).anim(3), (200, 40))]
        #elif type=='regular':     r=[self.screen.blit(ColoredText('qualification race', self.head_font).anim(3), (130, 40))]
        #else:                     r=[self.screen.blit(ColoredText('choose distance', self.head_font).anim(3), (140, 80))]
        r=[]

        for i,p in enumerate(players):
            if p is not None:
                p=p.upper()
                if isinstance(p, str):
                    players[i]=unicode(p,'utf')

        if all(players):
            vs=ColoredText('vs', font=self.head_font)
            r.append(self.screen.blit(vs.anim(2), (self.resolution[0]/2-vs.size[0]/2,
                                                  self.resolution[1]/2-vs.size[1]/2)))

            r += [ self._center(players[0],
                                self.resolution[1]/2-r[-1].height-self.head_font.get_height(), (0,0,255),
                                font=self.head_font),
                   self._center(players[1], self.resolution[1]/2+r[-1].height,
                                (255,0,0), font=self.head_font) ]
        else:
            which=players[1] and 1 or 0
            r.append(self._center(players[which], color=(which and (255,0,0) or (0,0,255)),
                                  font=self.head_font))

        pygame.display.update(r)

    def banner(self, txt):
        pygame.display.update(self._center(txt, color=(255,255,0), outline=10))
        pygame.time.wait(500)

    def _start_intro(self, text="", time=500, paint_back_f=None):
        self.clock.tick()
        if isinstance(text, pygame.Rect) and paint_back_f:
            paint_back_f()
            rect=text
            pygame.display.update(rect)
            pygame.time.delay(time-self.clock.tick())
        else:
            #pygame.draw.circle(self.screen, (255,255,0), (self.resolution[0]/2, self.resolution[1]/2),10)
            head=GradientText(100, text, self.huge_font, [(255,)*3, (255,255,0)])
            wait=0
            while wait<=time:
                wait+=100
                head_surf=head.anim()
                rect=self.screen.blit(head_surf,
                                      (self.resolution[0]/2-head_surf.get_width()/2,
                                       self.resolution[1]/2-head_surf.get_height()/2))
                pygame.display.update(rect)
                wait_now=100-self.clock.tick()
                pygame.time.delay(wait_now)

        return rect

    def finish(self, results):
        pygame.time.wait(2000)
        self._transition()
        for i,r in enumerate(results):
            if r[1]:
                if isinstance(r[1], str): r[1]=unicode(r[1],'utf')
                l=self._center(r[1].upper(), y=((results[0][1] and results[1][1]) and \
                                  i*200+65
                                  or 160),
                               color=(i and (255,0,0) or (0,0,255)), font=self.head_font)
                if r[0] is None:
                    res='n/q'
                elif r[0].is_integer():
                    res = '{:.0f}'.format(r[0])
                else:
                    res='{0:.3f}'.format(r[0])
                l=self._center(res, y=l.bottom, color=(255,255,255))
                if r[0] and r[2]>0:
                    self._center('curr pos: '+str(r[2]), y=l.bottom-20, color=(100,)*3, font=self.head_font)
        pygame.display.update()

    def show_results(self, qualified_times, title="results", next_screen_wait=5000, repeat=True):
        self.abort.clear()
        pygame.time.wait(200)
        head=ColoredText(title, font=self.font)

        def wait_to_clr(next_screen_wait=next_screen_wait):
            wait=0
            while wait<=next_screen_wait:
                if self.abort.is_set(): return True
                pygame.display.update(self.screen.blit(head.anim(),
                                                       (self.resolution[0]/2-head.size[0]/2, 10)))
                wait+=100
                pygame.time.wait(100)

            return False

        def run_once(qualified_times=qualified_times, title=title, next_screen_wait=next_screen_wait,
                     head=head, repeat=repeat):
            self._transition()
            y_pos=1
            for i,t in enumerate(qualified_times, 1):
                if i%2==0:
                    self.screen.fill((50,50,50), (20, 70+y_pos*40-5, 600, 40))
                self.screen.blit(self.head_font.render('{0: >2}. '.format(i), False, (255,255,0)),
                                 (22, 70+y_pos*40))
                if isinstance(t[1]['name'], str): t[1]['name']=unicode(t[1]['name'], 'utf')
                self.screen.blit(self.head_font.render(u'{0: <15}'.format(t[1]['name'].upper()),
                                                       False, (255,)*3),
                                 (100, 70+y_pos*40))
                self.screen.blit(self.head_font.render('{0: >6.2f}'.format(t[0]), False, (255,255,0)),
                                 (465, 70+y_pos*40))
                pygame.display.update([self.screen.blit(head.anim(),
                                                        (self.resolution[0]/2-head.size[0]/2, 10)),
                                       (20, 70+y_pos*40-5, 600, 40)])
                y_pos+=1
                pygame.time.wait(100)

                if i%8==0 and i<len(qualified_times):
                    if wait_to_clr(next_screen_wait): return False
                    #pygame.display.update(self.screen.fill((0,0,0), (0,100, 640, 340)))
                    self._transition()
                    rect_used=pygame.Rect(0,120,0,0)
                    y_pos=1

            if wait_to_clr(next_screen_wait): return False

            return repeat

        while run_once(): pass
        self.abort.clear()

    def show(self, msg, title=''):
        self.screen.fill((0,0,0))
        self._center(title, y=10)
        pygame.display.update()
        pygame.time.wait(200)

        if type(msg)==str:
            pygame.display.update(self._center(msg, font=self.head_font))
        else:
            for i,r in enumerate(msg):
                pygame.display.update(self._center(r, color=(255,255,255), y=self.resolution[1]/3+i*30,
                                                   font=self.head_font))
                pygame.time.wait(100)

    def quit(self): pygame.display.quit()


class ClientVis(Visualize):
    "Visualizng menus and interface for client side"
    cursor_r=None
    key_CURR=0
    key_PREV=-1
    key_NEXT=1
    key_UP=-19
    key_DOWN=19

    def __init__(self, *args, **kwargs):
        Visualize.__init__(self, *args, **kwargs)

        pygame.time.set_timer(pygame.USEREVENT+1, 1000) # for blinking cursor
        self.inputs = [ pygame.Rect(120, 150, 400, 42),
                        pygame.Rect(120, 300, 400, 42) ]

        self.input_size=[26,5]
        self.clock=pygame.time.Clock()

        self.keycodes=range(65,91)+range(48,58)+[95,47]
        self.curr_keycode=0

    def anim_cursor(self, focus, pos=0, show=False, hide=False):
        def paint_cursor():
            return self.screen.fill((focus and (255,0,0) or (0,0,255)),
                                           (self.inputs[focus].left+self.input_size[0]*pos+5,
                                            self.inputs[focus].bottom-self.input_size[1]-5,
                                            self.input_size[0], self.input_size[1]))
        if self.cursor_r:
            pygame.display.update(self.screen.fill((0,0,0), self.cursor_r))
            self.cursor_r=None
            if hide: return
        elif (1+pos)*self.input_size[0]<self.inputs[focus].width:
            self.cursor_r=paint_cursor()
            pygame.display.update(self.cursor_r)
        if show and not self.cursor_r and (1+pos)*self.input_size[0]<self.inputs[focus].width:
            self.cursor_r=paint_cursor()
            pygame.display.update(self.cursor_r)

    def sponsors(self):
        self._transition()
        t=GradientText(10, 'peace to our supportters', self.head_font, [(255,255,255), (0,0,0)])

        self.screen.fill((0,)*3, (0,0, 640, 100))
        self._center('support', font=self.font, color=(50,)*3, y=10)
        pygame.display.update((0,0,640,100))

        img=pygame.image.load(os.path.join(BASE_DATA_PATH, 'sponsors', 'sponsors3.png')).convert()
        img_ar=pygame.surfarray.array2d(img)
        pixel_ar=img_ar.copy()
        #pixel_ar.resize(map(lambda x: x%2==0 and x or x-1, pixel_ar.shape))
        self
        for step in range(19):
            step=20-step
            for x in range(0,pixel_ar.shape[0], step):
                if x+step<pixel_ar.shape[0]:
                    pixel_ar[x:x+step,::]=img_ar[x+step/2,::]
            pixel=pygame.Surface(pixel_ar.shape)
            pygame.surfarray.blit_array(pixel, pixel_ar)
            pygame.display.update(self.screen.blit(pixel, (0,100)))

            pygame.time.wait(100)

        pygame.display.update(self.screen.blit(img,(0,100)))


    def show_inputs(self):
        self._transition()

        #self.screen.fill((0,0,0))
        self._center('new race', y=20)

        for i in self.inputs:
            self.screen.fill((0,)*3,i)
            pygame.draw.rect(self.screen, (255,255,255), i, 1)

        pygame.display.update()

    def show_sets(self, sets, focus=2, highlight=0):
        x=self.inputs[0].left
        for j,s in enumerate(sets):
            for k,i in enumerate(self.inputs):
                if focus==2 or focus==k:
                    r=(x, i.bottom, self.input_size[0]*len(s)+10, i.height-10)
                    if j==highlight:
                        self.screen.fill((255,255,255), r)
                        txt_surf=self.head_font.render(s, False, (0,0,0))
                    else:
                        self.screen.fill((0,0,0), r)
                        txt_surf=self.head_font.render(s, False, (255,255,255))
                    self.screen.blit(txt_surf, (x+5, i.bottom+5))
            x+=self.input_size[0]*len(s)+10

        pygame.display.update()

    def switch_virt_keyboard(self, focus=0, key_offset=key_CURR):
        x=self.inputs[focus].left-60
        y=self.inputs[focus].bottom

        self.curr_keycode+=key_offset
        if self.curr_keycode<0: self.curr_keycode=0
        if self.curr_keycode>=len(self.keycodes): self.curr_keycode=len(self.keycodes)-1

        for i in self.keycodes:
            c_surf=self.head_font.render(chr(i), False, i==self.keycodes[self.curr_keycode] and (0,)*3 or (255,)*3,
                                         i==self.keycodes[self.curr_keycode] and (255,)*3 or (0,)*3)
            r=self.screen.blit(c_surf, (x,y))
            pygame.draw.rect(self.screen, (255,)*3, r.inflate(4,1), 1)
            x=r.right+4
            if i==83:
                y=r.bottom+1
                x=self.inputs[focus].left-60

        r_focused = (self.inputs[focus].left-62, self.inputs[focus].bottom, 600, 90)
        r_another = (self.inputs[int(not focus)].left-62, self.inputs[int(not focus)].bottom, 600, 90)
        self.screen.fill((0,)*3, r_another)
        pygame.display.update((r_focused,r_another))

    def print_names(self, focus, name):
        self.screen.fill((0,)*3, self.inputs[focus].inflate(-2,-2))
        self.screen.blit(self.head_font.render(name.upper(), False, focus and (255,0,0) or (0,0,255)),
                         (self.inputs[focus].left+5, self.inputs[focus].top+1))
        pygame.display.update(self.inputs[focus])

    def write_down(self, txt, y):
        so_far=''
        r=None
        for c in txt:
            so_far+=c
            pygame.time.wait(100)
            if r:
                pygame.display.update(self.screen.fill((0,0,0), r))
            r=self._center(so_far, y=y, font=self.head_font, color=(50,50,50))
            pygame.display.update(r)

    def press_enter(self):
        pygame.display.update(self._center('press enter', font=self.head_font, y=440, color=(255,255,255)))

    def repaint_dist_widg(self):
        self.screen.fill((0,)*3, (0, 360, 640, 440))

        #self.chain_gif.render(self.screen, (100, 350))

        self._center('dist: {0}'.format(self.dist), y=370)
        pygame.display.update((0, 360, 640, 440))


class GameVis(ClientVis):
    "Game engine itself to visualize progress of the race"

    players=[False,False]

    def __init__(self, *args, **kwargs):
        ClientVis.__init__(self, *args, **kwargs)

        self.layers= [ Layer('TLO.png', height=20), Layer('BUDYNKI.png', height=210),
                  Layer('CHODNIK.png'), Layer('DROGA.png') ]
        self.world=LayersStack(self.screen, self.layers)

        if self.unit is None: self.unit = float(self.resolution[0]-20)/self.dist

        # fixme: take into account different sprite width?
        self.screen_half_segm = self.resolution[0]/2-10-64

        self.riders=[ Rider('punkniebieski.png', 8,1, [10, 260]),
                      Rider('punkczerwony.png', 8,1, [10, 320]) ]

    def set_dist(self, d):
        self.dist=d
        #self.unit = float(self.resolution[0]-20)/self.dist

    def set_unit(self, u):
        self.unit=u
        #self.dist = float(self.resolution[0]-20)/self.unit

    def start(self, players=(True, True)):
        self.players=players
        self._transition()

        self.screen.fill((0,0,0), (0, 440, 640, 40))
        self.world.paint(0)

        for i,p in enumerate(players):
            if p:
                self.riders[i].reset()
                self.screen.blit(self.riders[i].img_surf, self.riders[i].pos,
                                 self.riders[i].show())



        self.speed=[0,0]

        #  pygame.draw.rect(self.screen, (255,255,255), (20, 445, 600, 10), 1)
        #  pygame.draw.rect(self.screen, (255,255,255), (20, 465, 600, 10), 1)

        pygame.display.update()

        self._start_intro(self._start_intro("3", 1000), time=500, paint_back_f=self.world.paint)
        self._start_intro(self._start_intro("2", 1000), time=500, paint_back_f=self.world.paint)
        self._start_intro(self._start_intro("1", 1000), time=500, paint_back_f=self.world.paint)

        self.go_banner=ColoredText('GO', font=self.huge_font, scale=5)

        pygame.display.update(self.screen.blit(self.go_banner.anim(),
                                               (self.resolution[0]/2-self.go_banner.size[0]/2,
                                                self.resolution[1]/2-self.go_banner.size[1]/2)))
        #self.clock=pygame.time.Clock()
        self.millis_from_start=0

    def update_race(self, player, pos, speed=0, time=0):
        wrld_speed=0
        other=int(not player)
        self.speed[player]=speed

        if abs(self.riders[player].pos[0]-self.screen_half_segm)>self.unit or \
                self.dist-pos < self.screen_half_segm/self.unit:
            self.riders[player].pos[0]+=self.unit
        else:
            wrld_speed=-self.unit
            #self.players_pos[other]-=self.unit

        self.world.paint(wrld_speed)

        for i,p in enumerate(self.players):
            if p:
                self.screen.blit(self.riders[i].img_surf, self.riders[i].pos,
                                 i==player and self.riders[i].cycle() or self.riders[i].show())
                self.screen.blit(self.head_font.render('{0: 5.1f} km/h'.format(self.speed[i]), False,
                                                       i and (255,0,0) or (0,0,255)), (10, 10+i*30))

        self.riders[other].pos[0]+=wrld_speed
        #self.screen.blit(self.head_font.render(str(.35/time), False, (255,255,255)), (20, 20+player*40))

        self.millis_from_start+=self.clock.tick()
        if self.millis_from_start < 2000:
            self.screen.blit(self.go_banner.anim(),
                             (self.resolution[0]/2-self.go_banner.size[0]/2,
                              self.resolution[1]/2-self.go_banner.size[1]/2))
            self.screen.fill((0,)*3, (0,440,640,40))
            #  pygame.draw.rect(self.screen, (255,255,255), (20, 445, 600, 10), 1)
            #  pygame.draw.rect(self.screen, (255,255,255), (20, 465, 600, 10), 1)

        if time:
            self.screen.blit(self.head_font.render('T: {0: 5.2f}'.format(time), False, (255,255,255)),
                             (415, 20))

        self.screen.fill(player and pygame.color.THECOLORS['red'] or pygame.color.THECOLORS['blue'],
                         (22, 446+player*20, pos*600/self.dist-2, 7))

        pygame.display.update()


class SimplegameVis(GameVis):
    players = [False, False]

    def __init__(self, *args, **kwargs):
        #super(SimpleGameVis, self).__init__(*args, **kwargs)
        GameVis.__init__(self, *args, **kwargs)
        self.world = Background(self.screen, 'WSZYSYKO.png')

    def set_dist(self, d):
        self.dist = d

    def set_unit(self, u):
        self.unit = u

        wrld_speed = 0
        other = int(not player)
        self.speed[player]=speed

    def update_race(self, player, pos, dpos=1, speed=0, time=0, bars=True):
        #print player, pos, dpos, speed, time
        clock_tick = self.clock.tick()
        wrld_speed=0
        other=int(not player)
        self.speed[player]=speed

        if self.riders[player].pos[0] < self.screen_half_segm:
            self.riders[player].pos[0]+=self.unit*dpos
        else:
            wrld_speed=-self.unit*dpos
        self.riders[other].pos[0]+=wrld_speed

        self.world.paint(wrld_speed)
        for i,p in enumerate(self.players):
            if p:
                self.screen.blit(self.riders[i].img_surf, self.riders[i].pos,
                                i==player and dpos>0 and self.riders[i].cycle() or self.riders[i].show())
                self.screen.blit(self.head_font.render('{0: 5.1f} km/h'.format(self.speed[i]), False,
                                                    i and (255,0,0) or (0,0,255)), (10, 10+i*30))

        #self.screen.blit(self.head_font.render(str(.35/time), False, (255,255,255)), (20, 20+player*40))

        self.millis_from_start+=clock_tick
        if self.millis_from_start < 2000:
            self.screen.blit(self.go_banner.anim(),
                            (self.resolution[0]/2-self.go_banner.size[0]/2,
                            self.resolution[1]/2-self.go_banner.size[1]/2))
            self.screen.fill((0,)*3, (0,440,640,40))
            #  pygame.draw.rect(self.screen, (255,255,255), (20, 445, 600, 10), 1)
            #  pygame.draw.rect(self.screen, (255,255,255), (20, 465, 600, 10), 1)

        if time:
            self.screen.blit(self.head_font.render('T: {0: 5.2f}'.format(time), False, (255,255,255)),
                            (415, 20))

        if bars:
            self.screen.fill(player and pygame.color.THECOLORS['red'] or pygame.color.THECOLORS['blue'],
                            (0, 440+player*20, pos*640/self.dist, 20))
        else:
            self.screen.fill((0,)*3, (130+player*320, 446, 100, 50))
            self.screen.blit(self.head_font.render(str(pos), False, player and (255,0,0) or (0,0,255)),
                             (130+player*320, 446))

        pygame.display.update()



class BarVis(ClientVis):
    "Visualization of the race progress by two progress bars. Extremely simple"

    def __init__(self, *args, **kwargs):
        ClientVis.__init__(self, *args, **kwargs)
        self.bars= [ pygame.Rect(20,20, 600, 140),
                     pygame.Rect(20,300, 600, 140) ]

        self.set_dist(self.dist)

    def set_dist(self, d):
        self.dist=d
        self.unit=float(self.bars[0].width-10)/self.dist

    def set_unit(self, u):
        self.unit=u
        self.dist=float(self.bars[0].width-10)/self.unit

    def _back(self):
        self.screen.fill((0,0,0))
        pygame.draw.rect(self.screen, (255,255,255), self.bars[0], 2)
        pygame.draw.rect(self.screen, (255,255,255), self.bars[1], 2)

    def new_race(self, *args, **kwargs):
        Visualize.new_race(self, *args, **kwargs)

        self.screen.fill((0,)*3, (0,370,640, 110))
        self.screen.blit(self.head_font.render('when next screen appears', False,
                                               (50,)*3), (20, 370)),
        self.screen.blit(self.head_font.render('please dont pedal until', False,
                                               (50,)*3), (20, 400)),
        self.screen.blit(self.head_font.render('you\'ll see: ', False,
                                               (50,)*3), (20, 430)),
        self.screen.blit(self.head_font.render('GO', False, (255,255,0)),
                         (400,430))
        pygame.display.update((0,370,640, 110))

    def start(self, whatever=False):
        self._back()
        pygame.display.update()

        self._start_intro(self._start_intro("3", 1000), time=500, paint_back_f=self._back)
        self._start_intro(self._start_intro("2", 1000), time=500, paint_back_f=self._back)
        self._start_intro(self._start_intro("1", 1000), time=500, paint_back_f=self._back)

        pygame.display.update(self._center("GO", font=self.huge_font, color=(255,255,0)))
        self.go_cleared=False

    def update_race(self, player, pos, dpos=1, speed=0, time=0):
        r=[]

        if not self.go_cleared and time>=2:
            r.append(self._center('GO', font=self.huge_font, color=(0,0,0)))
            self._back()
            self.go_cleared=True

        r.append(self.screen.fill(player and (255,0,0) or (0,0,255),
                                  (self.bars[player].left+5, self.bars[player].top+5,
                                   pos*self.unit, self.bars[player].height-10)))
        if time:
            r.append(self._center('T:{0:05.2f}'.format(time), y=180, outline=2))

        pygame.display.update(r)


class CMWCClientVis(ClientVis):
    "Clent side visualization made for CMWC2k+11"

    def __init__(self, *args, **kwargs):
        ClientVis.__init__(self, *args, **kwargs)

        self.inputs = [ pygame.Rect(140, 150, 120, 110),
                        pygame.Rect(140, 300, 120, 110) ]

        self.num_font=pygame.font.Font(os.path.join(BASE_DATA_PATH, 'm08.TTF'), 90)
        self.input_size=list(self.font.size('9'))
        self.input_size[1]=5

    def show_inputs(self, focus=2):
        for k,i in enumerate(self.inputs):
            if focus==2 or focus==k:
                self.screen.fill((0,0,0), i)
                pygame.draw.rect(self.screen, (255,255,255), i, 2)
                self.screen.blit(self.head_font.render(k==0 and 'blue: ' or 'red: ',
                                                       False, k and (255,0,0) or (0,0,255)),
                                 (20, i.centery))

        pygame.display.update()

    def print_racenumber(self,focus, txt):
        self.show_inputs(focus)

        if self.cursor_r:
            pygame.display.update(self.screen.fill((0,0,0), self.cursor_r))
            self.cursor_r=None

        self.screen.blit(self.num_font.render(txt, False, focus and (255,0,0) or (0,0,255)),
                         (150, focus and 310 or 160))
        pygame.display.update(self.inputs[focus])

    def show_player(self, focus, player=None, msg=''):
        r=self.screen.fill((0,0,0), (self.inputs[focus].right, self.inputs[focus].top,
                                     self.resolution[0]-self.inputs[focus].right,
                                     self.inputs[focus].height))
        if player:
            self.screen.blit(self.head_font.render(unicode(player['name'], 'utf').upper(),
                                                   False, focus and (255,0,0) or (0,0,255)),
                             (280, self.inputs[focus].top))
        elif msg:
            self.screen.blit(self.head_font.render(msg, False, (255,255,255)),
                                                   (280, self.inputs[focus].top))
        pygame.display.update(r)



if __name__ == '__main__':

    vis = SimplegameVis((640,480), unit=1, dist=720, title='cmwc')
    vis.start()
    for i in range(515):
        vis.update_race(0, i)

    for i in range(600):
        vis.update_race(1,i)

#     vis.screen.fill((255,)*3)
#     pygame.display.flip()
#     vis.abort()

#    vis.show_results(results['male'])

#     t=GradientText(10, u'ŻĄŁĘDŹ', vis.font, [(0,0,255), (255,0,0)])
#     for s in range(80):
#         pygame.display.update(vis.screen.blit(t.anim(), (10, 10)))
#         pygame.time.wait(100)

    #vis.new_race(('karol_koralski', 'kaap'), type='third_place')
    #vis.sponsors()
    #vis.finish([[1.32, 'koral'], [None,None]])
    #vis.show_racenumber_inputs()
    #vis.start()
    pygame.time.wait(5000)


