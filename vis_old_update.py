
        
    def update_race(self, offset):
        wrld_speed=0
        better = self.players_pos[1]==self.players_pos and 1 or 0
        worse=int(not better)

        if abs(self.players_pos[better]-self.screen_half_segm)<self.unit:
            wrld_speed=-self.unit*offset[better]
        else:
            self.players_pos[better]+=self.unit*offset[better]
        self.players_pos[worse]+=self.unit*offset[worse]
        
        self.world.paint(wrld_speed)

        for i,p in enumerate(self.players):
            self.screen.blit(p.img_surf, (self.players_pos[i], 215+i*60),
                             i==player and p.cycle() or p.show())

        #self.screen.blit(self.head_font.render(str(.35/time), False, (255,255,255)), (20, 20+player*40))

        self.millis_from_start+=self.clock.tick()
        if self.millis_from_start < 2000:
            self._center('GO')
        
        self.screen.fill(player and color.THECOLORS['red'] or color.THECOLORS['blue'],
                         (22, 447+player*20, pos*600/self.dist-2, 7))
        pygame.display.update()



class TkinterVis(Thread):
    def __init__(self, vis):
        Thread.__init__(self)
        self.parent_vis=vis

    def _center(self, txt, color='white', size=50):
        return self.canvas.create_text(int(self.canvas['width'])//2, int(self.canvas['height'])//2,
                                       text=txt, fill=color, justify=CENTER,
                                       font=("Alpha Beta BRK", size))
        
    def run(self):
        self.master = Tk()
        self.master.bg='black'
        self.master.resizable(False,False)
        self.master.geometry('640x480+0+0')

        self.canvas = Canvas(self.master, width=640, height=480, bg='black')
        self.canvas.pack()

        self.master.bind('<<start>>', self.start_race)
        self.master.bind('<<abort>>', self.abort)
        self.master.bind('<<update>>', self.update_race)
        self.master.bind('<<finish>>', self.finish)
        
        self.master.mainloop()

    def new_race(self, players):
        self.players=players
        self.canvas.delete(ALL)
        self._center(all(players) and "{0}\n\nvs\n\n{1}".format(*players) or \
                     '{0}'.format(players[players[1] and 1 or 0]))

    def start_race(self, ev):
        print ev
        self.canvas.delete(ALL)
        self.canvas.create_rectangle(20, 20, 620, 220, outline="white")
        self.canvas.create_rectangle(20, 240, 620, 460, outline="white")
        self.master.update_idletasks()
        item=self._center("3")
        self.master.update_idletasks()
        sleep(1.4)
        self.canvas.delete(item)        
        item=self._center('2')
        self.master.update_idletasks()        
        sleep(1.4)
        self.canvas.delete(item)
        item=self._center('1')
        self.master.update_idletasks()        
        sleep(1.4)
        self.canvas.delete(item)

        self._center('GO')

    def abort(self):
        pass
        
    def update_race(self):
        pass

    def finish(self):
        pass
        
