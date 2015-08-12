import sys, csv
from time import time, sleep
from threading import Thread, Event
from copy import copy, deepcopy
from pickle import dump
from time import sleep
from math import ceil
import visualize
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR, SOCK_DGRAM, error as socket_error
from subprocess import Popen, PIPE

class Output:
    cmd_sockf = []
    def __init__(self, res, dist, unit, local_vis='', remote_vis='bar',
                 fullscreen=False, net='', of=None, ff=None, qiface=None):
        self.res=res
        self.dist=dist
        self.unit=unit
        self.vis=local_vis.split(',')
        self.fullscreen=fullscreen

        self.s=None
        self.primary_vis=None
        self.another_vis=None
        self.qiface=qiface
        self.of=None
        self.ff=None

        if net:
            net=net.partition(':')
            self.net=(net[0], int(net[2]))
            self.s=socket(AF_INET, SOCK_DGRAM)
            self.s.connect(self.net)
            self.s.settimeout(3)
            connected=False
            while not connected:
                print('trying to connect to vis endpoint: {0}'.format(self.net))
                try:
                    self.s.send('__try')
                    self.s.recv(40).startswith('__catch')
                except socket_error, e:
                    sleep(3)
                    continue
                else:
                    print('connection with vis endpoint established')
                    connected=True
                    #print('socket error'+str(e))

            self.s.send('new_main({0}, {1}, {2}, "{3}", {4})\n'.format(res,dist,unit,remote_vis,fullscreen))
        if local_vis:
            self.primary_vis=getattr(visualize,self.vis[0].capitalize()+'Vis')(res, dist, unit, fullscreen, 'primary')
            self.another_vis=None
            if len(self.vis)==2:
                python_interpreter = sys.platform=='win32' and 'python.exe' or 'python'
                self.another_vis=Popen([python_interpreter,'child.py',
                                        self.vis[1].capitalize()+'Vis((640,480),'+','.join(map(str, [dist, unit, int(fullscreen)]))+\
                                        ',"secondary")'], stdin=PIPE)

        if of is not None:
            self.of_f=open(of, 'a')
            self.of=csv.writer(self.of_f)

        if ff is not None:
            self.ff=open(ff, 'w')

    def addcmd_sockf(self, f):
        self.cmd_sockf.append(f) # SOME fallback on sock shutdown :/

    def abort(self):
        if self.s: self.s.send('out.abort()\n')
        if self.primary_vis: self.primary_vis.abort.set()

    def new_race(self, players, type_='regular'):
        s='new_race([{0}, {1}], "{2}")\n'.format(*([ p and '"'+p+'"' or '""' for p in players ]+[type_]))

        if self.s: self.s.send('out.'+s)
        if self.qiface: self.qiface.new_race.emit(*players)
        if self.another_vis: self.another_vis.stdin.write('vis.'+s)
        if self.primary_vis: self.primary_vis.new_race(players, type_)

    def start(self, players=(True, True)):
        if self.s: self.s.send('out.start(({0}, {1}))\n'.format(*[ p and '"'+p+'"' or '""' for p in players ]))
        if self.qiface: self.qiface.start.emit()
        if self.another_vis: self.another_vis.stdin.write('vis.start()\n')
        if self.primary_vis: self.primary_vis.start(players)

    def update_race(self, player, pos, dpos, speed=0, time=0):
        args=(player, pos, dpos, speed, time)
        s='update_race{0}\n'.format(args)

        if self.s: self.s.send('out.'+s)
        if self.qiface: self.qiface.update_race.emit(*args)
        if self.another_vis: self.another_vis.stdin.write('vis.'+s)
        if self.primary_vis:
            #Thread(target=self.primary_vis.update_race, args=args).start()
            self.primary_vis.update_race(*args)

    def finish(self, results):
        if self.qiface:
            if any(map(lambda x : isinstance(x[0], float), results)):
                self.qiface.finish.emit(*[ r[0] or 9999999 for r in results ]) # ugly hack FIXME

        if self.s: self.s.send('out.finish({0})\n'.format(results))
        if self.another_vis: self.another_vis.stdin.write('vis.finish({0})\n'.format(results))
        if self.primary_vis: self.primary_vis.finish(results)

        for f in self.cmd_sockf:
            f.write('finish.\r\n')

    def banner(self, txt):
        if self.qiface and txt in('aborted','false start', 'error'): self.qiface.abort.emit()
        if self.s: self.s.send('out.banner("{0}")\n'.format(txt))
        if self.another_vis: self.another_vis.stdin.write('vis.banner("{0}")\n'.format(txt))
        if self.primary_vis: self.primary_vis.banner(txt)

    def set_dist(self, dist):
        if self.s: self.s.send('out.set_dist({0})\n'.format(dist))
        if self.another_vis: self.another_vis.stdin.write('vis.set_dist({0})\n'.format(dist))
        if self.primary_vis: self.primary_vis.set_dist(dist)

    def set_unit(self, unit):
        if self.s: self.s.send('out.set_unit({0})\n'.format(unit))
        if self.another_vis: self.another_vis.stdin.write('vis.set_unit({0})\n'.format(unit))
        if self.primary_vis: self.primary_vis.set_unit(unit)

    def sponsors(self):
        if self.s: self.s.send('out.sponsors()\n')
        if self.primary_vis: self.primary_vis.sponsors()

    def _gather_res(self, t):
        pass

    def show_results(self, qualified_times=None, title="results", next_screen_wait=5000, repeat=True):
        if self.s:
            self.s.send('gathered_t=[]')
            for t in qualified_times:
                self.s.send('gathered_t.append({0})'.format(t))
            self.s.send('out.show_results(self.gathered_t, "{0}", {1}, {2})'.format(title, next_screen_wait, repeat))
        if self.primary_vis:
            Thread(target=self.primary_vis.show_results,
                   args=(qualified_times, title, next_screen_wait, repeat)).start()

    def write(self, result):
        if self.of:
            self.of.writerow([result[0]]+result[1].values())
            self.of_f.flush()

    def write_finals(self, f_tables):
        if self.ff:
            dump(f_tables, self.ff)

    def quit(self):
        if self.s: self.s.send('out.quit()\n')
        if self.primary_vis: self.primary_vis.quit()
        if self.another_vis is not None: self.another_vis.stdin.write('sys.exit()\n')
        if self.of is not None: self.of_f.close()
        if self.ff is not None: self.ff.close()


class Race(Thread):
    def __init__(self, gs, players, race_type='regular'):
        Thread.__init__(self)
        self.gs=gs
        self.type=race_type
        self.players=list(players)
        self.gs.race_is_runing=False
        self.gs.race=self

        self.player_names = [ p and p['name'] for p in players ]
        self.gs.out.new_race(self.player_names, self.type)

    def swap_players(self):
        self.players.reverse()
        self.player_names.reverse()

        self.gs.out.new_race(self.player_names, self.type)

    def run(self):
        self.gs.race_is_runing=True
        self.gs.dev.clean()
        self.gs.out.start(self.player_names)

        if not self.gs.out.primary_vis: sleep(3)

        curr_dist = [ not self.players[0] and self.gs.dist or 0,
                      not self.players[1] and self.gs.dist or 0 ]

        e_inf=self.gs.dev.check()
        if e_inf=='false start':
            self.gs.abort.set()

        start_time=time()
        deltatime=0
        between_time=[start_time,start_time]
        between_dist=[0,0]
        speed=[0,0]

        results=[None, None]

        #import yappi
        #yappi.start()
        while min(curr_dist)<self.gs.dist:
            if self.gs.abort.is_set():
                self.gs.abort.clear()
                self.gs.out.banner(e_inf or 'aborted')
                return self.end_race(results)

            p = self.gs.dev.cycle()
            if not p in (0, 1):
                continue
            #if p==-2:
                #self.gs.abort.set()
                #e_inf='error'
                #continue

            if self.players[p] and curr_dist[p]<self.gs.dist:
                curr_time=time()
                curr_dist[p]+=1

                if curr_time-between_time[p]>self.gs.sample_t:
                    speed[p]=3600*self.gs.roller_circum*self.gs.dev.threshold*(curr_dist[p]-between_dist[p])\
                                /float(curr_time-between_time[p])
                    deltatime=curr_time-start_time
                    self.gs.out.update_race(p, curr_dist[p],
                                            curr_dist[p]-between_dist[p],
                                            speed=speed[p], time=deltatime)
                    between_time[p]=curr_time
                    between_dist[p]=curr_dist[p]

                #self.gs.out.update_race(p, curr_dist[p])
                if curr_dist[p]==self.gs.dist:
                    results[p]=curr_time-start_time

        #yappi.get_func_stats().print_all()
        #yappi.get_thread_stats().print_all()
        #yappi.stop()
        return self.end_race(results)

    def end_race(self, results):
        self.gs.race_is_runing=False

        pos=self.gs.collect_race(map(list, zip(results, self.players)), self.type)
        self.gs.out.finish(map(list, zip(results, self.player_names, pos)))

        return zip(results, self.players)


class Race2(Race):
    def run(self):
        self.gs.race_is_runing=True
        self.gs.dev.clean()
        self.gs.out.start(self.player_names)

        if not self.gs.out.primary_vis: sleep(3)

        curr_dist = [ not self.players[0] and self.gs.dist or 0,
                      not self.players[1] and self.gs.dist or 0 ]

        e_inf=self.gs.dev.check()
        if e_inf=='false start':
            self.gs.abort.set()

        start_time=time()
        deltatime=0
        between_time=[start_time,start_time]
        avg_between_time=[start_time,start_time]
        avg_between_dist = [0,0]
        between_dist=[0,0]
        speed=[0,0]

        results=[None, None]

        #import yappi
        #yappi.start()
        p = 0
        while min(curr_dist)<self.gs.dist:
            p = int(not p)

            if self.gs.abort.is_set():
                self.gs.abort.clear()
                self.gs.out.banner(e_inf or 'aborted')
                return self.end_race(results)

            if self.players[p] and curr_dist[p]<self.gs.dist:
                curr_time=time()
                dtime=curr_time-between_time[p]
                if dtime > self.gs.sample_t:
                    curr_dist[p] = self.gs.dev.dist(p)
                    dpos = curr_dist[p]-between_dist[p]
                    if dpos>0:
                        if curr_time-avg_between_time[p]> 2.5: # upd speed every 2.5 sec.
                            speed[p] = 3600*self.gs.roller_circum*self.gs.dev.threshold*(curr_dist[p]-avg_between_dist[p])/(curr_time-avg_between_time[p])
                            avg_between_time[p]=curr_time
                            avg_between_dist[p] = curr_dist[p]

                        self.gs.out.update_race(p, curr_dist[p], dpos, speed[p],
                                                curr_time-start_time)
                        between_dist[p]=curr_dist[p]
                    between_time[p]=curr_time

                if curr_dist[p]>=self.gs.dist:
                    results[p]=curr_time-start_time

        #yappi.get_func_stats().print_all()
        #yappi.get_thread_stats().print_all()
        #yappi.stop()
        return self.end_race(results)


class Goldsprints:
    max_speed = []
    race=None
    sets=False

    race_is_runing=False
    race_is_finished=False

    def __init__(self, out, dev, dist, unit, sample_t, roller_circum, sets=['_']):
        self.out = out
        self.dev = dev
        self.dist = dist
        self.unit = unit
        self.sample_t = sample_t
        self.roller_circum = roller_circum

        self.start = Event()
        self.abort = Event()
        self.quit = Event()

        self.sets=sets

        self.times = dict([(s, []) for s in self.sets])
        self.best_times= dict([(s, []) for s in self.sets])
        self.finals_worse= dict([(s, []) for s in self.sets])
        self.finals_better= dict([(s, []) for s in self.sets])
        self.finals_results= dict([(s, []) for s in self.sets])
        self.finals_curr= dict([(s, []) for s in self.sets])

    def collect_race(self, results, race_type):
        pos=[0, 0]
        single_rset = None
        if results[0][0] and results[1][0] and results[0][1]['set']==results[1][1]['set']:
            single_rset = results[0][1]['set']

        for r in results:
            if r[0]:
                rset=r[1]['set']
                self.times[rset].append(r)
                self.out.write(r)
                if single_rset is None:
                    self.best_times[rset] = self._gen_bt(rset)

        if single_rset:
            self.best_times[single_rset] = self._gen_bt(single_rset)

        for i,r in enumerate(results):
            pos[i]=self.get_current_pos(r[1]['name'], r[1]['set'])


        if race_type.startswith('final') and len(results)==2 and any([r[0] for r in results]):
            pos=[0,0]
            self.collect_finals_race(results)

        self.race=None
        return pos

    def get_current_pos(self, name, rset):
        for i,t in enumerate(self.best_times[rset], 1):
            if t[1]['name']==name:
                return i
        return -1

    def collect_finals_race(self, results):
        rset=results[0][1]['set']
        results.sort()
        if results[0][0]==None:results.reverse()

        if self.finals_curr[rset] in (self.finals_better[rset], self.finals_worse[rset]):
            self.finals_results[rset]=results+self.finals_results[rset]
        else:
            if results[0][1]['pos']>len(self.finals_better[rset]): # trying find valid position where
                for i,p in enumerate(reversed(self.finals_better[rset])): # we can save corresponding race
                    if p is None: break
                results[0][1]['pos']=len(self.finals_better[rset])-i-1

            print len(self.finals_better[rset]), results[0][1]['pos']
            self.finals_better[rset][results[0][1]['pos']]=results[0] # add better to next round
            self.finals_worse[rset].append(results[1])                # add worse to further results

        print self.finals_curr[rset]
        self.out.write_finals([ (a , getattr(self, a)) for a in dir(self) if a.startswith('finals_') ])

    def begin_final_round(self, rset, vis=False):
        if self.finals_worse[rset]==self.finals_curr[rset]:
            self.finals_curr[rset]=self.finals_better[rset]
            title='final'
        else:
            self.finals_curr[rset]=self.finals_worse[rset]
            title='3rd place'

        msg=['{0[1][name]} vs {1[1][name]}'.format(*self.finals_curr[rset]) ]
        if vis:
            self.out.show(msg, title='{0} {1}'.format(rset, title))

        return msg

    def begin_round(self, rset, vis=False):
        if len(self.finals_better[rset])==2:
            return self.begin_final_round(rset, vis)


        self.finals_worse[rset].sort()
        for r in self.finals_worse[rset]:
            if r[0] is None: self.finals_worse[rset].append(self.finals_worse[rset].pop(0))
            else: break

        self.finals_curr[rset]=copy(self.finals_better[rset])
        self.finals_results[rset]=copy(self.finals_worse[rset])+self.finals_results[rset]
        self.finals_better[rset]=[None]*(len(self.finals_better[rset])//2)
        self.finals_worse[rset]=[]

        if vis:
            self.out.show_results(self.finals_curr[rset], title="qualified: {0}".format(rset))

        return self.f_races_in_round(rset)

    def _gen_bt(self, rset, n=0):
        tt=deepcopy(sorted(self.times[rset]))
        btt=[]
        i=0
        for t in tt:
            for bt in btt:
                if bt[1]['name']==t[1]['name']:
                    break
            else:
                t[1]['pos']=i
                i+=1
                btt.append(t)
                if len(btt)==n: return btt

        return btt

    def choose_best(self, num_of_players=8, rset=''):
        if rset:
            t=self._gen_bt(rset)
            self.best_times[rset]=t[num_of_players:]
            self.finals_better[rset]=t[:num_of_players]
            return self.finals_better[rset]
        else:
            for s in self.sets:
                t = self._gen_bt(s)
                self.best_times[s]=t[num_of_players:]
                self.finals_better[s]=t[:num_of_players]
            return self.finals_better

    def f_get_racers(self, players, rset):
        racers=[]
        i_to_del=[]
        for p in players:
            for i,k in enumerate(self.finals_curr[rset]):
                if p==k[1]['name']:
                    racers.append(deepcopy(k[1]))
                    break
            else:
                return '{0} out of scope'.format(p)

        return racers

    def f_races_in_round(self, rset, vis=False):
        msg=[]
        start=0
        stop=len(self.finals_curr[rset])
        if stop%2==1:
            msg.append('{0[1][name]} has no oponent'.format(self.finals_curr[rset][0]))
            start=1
            stop+=1
        stop/=2
        for r in zip(self.finals_curr[rset][start:stop],
                         reversed(self.finals_curr[rset])):
            r[1][1]['pos']=r[0][1]['pos']
            msg.append('{0[1][name]: <14}vs{1[1][name]: >14}'.format(*r))

        if vis:
            self.out.show(msg, title='{0} upcoming races'.format(rset))

        print self.finals_curr[rset]

        return msg

    def f_cancel_race(self, rset, players):
        msg=''
        for p in players:
            for i in range(len(self.finals_better[rset])):
                if p==self.finals_better[rset][i][1]['name']:
                    self.finals_curr[rset].append(self.finals_better[rset].pop(i))
                    break
                if i<len(self.finals_worse[rset]) and p==self.finals_worse[rset][i][1]['name']:
                    self.finals_curr[rset].append(self.finals_worse[rset].pop(i))
                    break
                if i<2 and len(self.finals_better[rset])<=1 and p==self.finals_results[rset][i][1]['name']:
                    self.finals_curr[rset].append(self.finals_results[rset].pop(i))
                    break
            else: msg+='{0} not found\r\n'.format(p) # what if only 1 is found?

        return msg or 'ok.'

    def f_replace(self, rset, org, subst=None):
        for p in self.finals_curr[rset]:
            if org==p[1]['name']:
                org=p
                for p in self.finals_curr[rset][org[1]['pos']+1:]:
                    p[1]['pos']-=1
                    self.finals_curr[rset][p[1]['pos']]=p
                break
        else: return '{0} out of scope'.format(org)

        self.finals_curr[rset].pop()
        if ceil(float(len(self.finals_curr[rset]))/2)<len(self.finals_better[rset]):
            self.finals_better[rset].pop()

        msg=''
        if subst:
            msg=self.f_add(rset, subst)
        if not msg:
            self.finals_results[rset].insert(0, org)
            msg='ok'
        return msg

    def f_add(self, rset, pl):
        for i,p in enumerate(self.finals_worse[rset]):
            if pl==p[1]['name']:
                pl=self.finals_worse[rset].pop(i)
                break
        else:
            for i,p in enumerate(self.finals_results[rset]):
                if pl==p[1]['name']:
                    pl=self.finals_results[rset].pop(i)
                    break
            else:
                for i,p in enumerate(self.best_times[rset]):
                    if pl==p[1]['name']:
                        pl=self.best_times[rset].pop(i)
                        break
                else: return '{0} out of scope'.format(pl)

        pl[1]['pos']=len(self.finals_curr[rset])
        self.finals_curr[rset].append(pl)

        if ceil(float(len(self.finals_curr[rset]))/2)>len(self.finals_better[rset]):
            self.finals_better[rset].append(None)

        return 'ok'

    def f_promote(self, rset, pl, pos=-1):
        for p in self.finals_curr[rset]:
            if p[1]['name']==pl:
                if pos<0: pos=p[1]['pos']
                else: p[1]['pos']=pos

                if self.finals_better[rset][pos] is None:
                    self.finals_better[rset][pos]=p
                else:
                    return 'position is already engaged'
                break
        else:
            return '{0} out of scope'.format(pl)

        return 'ok'


class CMWCGoldsprints(Goldsprints):
    def __init__(self, players_f, *args, **kwargs):
        Goldsprints.__init__(self, *args, **kwargs)
        self.players=self.load_participants(open(players_f))

    @staticmethod
    def load_participants(f):
        players=[None]*1000
        for p in csv.DictReader(f):
            if not int(p['guest']):
                del p['guest']
                if p['_nickname']:
                    p['name']=p['_nickname']
                else:
                    p['name']=p['_firstname']+'_'+p['_lastname']
                players[int(p['__race_number'])]=p

        return players


if __name__ == "__main__":
    pass
