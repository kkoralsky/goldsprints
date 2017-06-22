from goldsprints import Race, Race2
from device import DoubleBluetoothDev, BluetoothDev

import socket, sys
from threading import Thread
from inspect import getargspec

from PySide import QtCore

class Commands(QtCore.QObject):
    msg=[]
    results=[]
    race_q=[]
    def __init__(self, gs):
        QtCore.QObject.__init__(self)
        self.gs=gs

    def help(self):
        return """
new_race [<blue>] <red> \     - prepare new qualification race between <blue>
         [<bset>] [<rset>]      and <red>; if no actual set (<rset> and/or
 / r [<blue>] <red>  \          <bset>) is given: chooses first set used in
     [<rset>] [<bset>]          current runtime
add_race [<blue>] <red> \     - add race to the queue (it will be started as
         [<bset>] [<rset>]      soon as 'next_race' will be executed
next_race                     - pop the oldest planned race from the queue
swap                          - swap players
start / s                     - start race
abort / a                     - abort race
begin_finals [<set>] [<n=8>]\ - choose <n> best times of <set>, (or all sets if
            [<show=f>]          not given); <n> can be: 4, 8, 16 or 32
next_round / n <set>          - start new round of <set> finals
final_race <blue> <red> <set> - start new race in finals; racers should belong
 / f <blue> <red> <set>         to current round in finals (ask 'show_remaining'
                                if in doubt)
replace <set> <org> <subst>   - disqualify <org> racer from finals and replace
                                him with <subst> (either from loser qualified
                                players or from not qualified players)
show_remaining <set> \        - show remaining races in current round for <set>
               [<public=t>]
show_times [<set>] \          - show qualification times; optional <set> can
           [<public=f>]         concrete the results
show_results [<set>] [<n>] \  - show <n> best results of <set>, if no <n>
             [<public=t>] \     is given, shows all results of either
             [<whole=f>]        qualifications or finals if they are actually
                                started; optional <whole> argument states if
                                command should show both finals and qualifications
                                results at one time
set_dist <d> [<set>]          - set the distance to <d> for <set>
quit                          - abort runing race if needed and quit"""
    def _check_r(self, blue, red, b_set, r_set):
        msg=''
        if (blue and len(blue)>15) or (red and len(red)>15):
            msg+='too long names\r\n'
        if not (blue or red):
            msg+='give at least 1 player\r\n'
        if b_set and b_set not in self.gs.sets:
            msg+='blue player set not found'
        if r_set and r_set not in self.gs.sets:
            msg+='red playet set not found'

        return msg

    @QtCore.Slot(str, str, str, str, result=str)
    def new_race(self, blue=None, red=None, b_set=None, r_set=None):
        """prepare new qualification race between <blue> if no actual set (<r_set> and/or <b_set>)
        is given: chooses first set used in current runtime"""
        msg=self._check_r(blue, red, b_set, r_set)
        if msg: return msg
        elif  self.gs.race_is_runing: return 'race is actually running; try: add_race'
        else:
            attrs = (self.gs,(blue and {'name':blue, 'set':b_set or self.gs.sets[0]},
                     red and {'name':red, 'set':r_set or self.gs.sets[0]}))
            if hasattr(self.gs.dev, 'dist'):
                Race2(*attrs)
            else:
                Race(*attrs)
            return "{0} (blue) and {1} (red)".format(blue, red)

    def r(self, *args, **kwargs):
        return self.new_race(*args, **kwargs)

    @QtCore.Slot(str,str,str)
    def finals_race(self, blue, red, rset='_'):
        if not rset in self.gs.sets:
            return '{0}: not such set'.format(rset)
        if blue and red:
            players=self.gs.f_get_racers((blue,red),rset)
            if type(players)==str:
                return players
            else:
                Race(self.gs, players, race_type='finals')

                return "{0} (blue) and {1} (red)".format(blue, red)
        else:
            return 'both racers have to be given'


    def f(self, *args, **kwargs):
        return self.finals_race(*args, **kwargs)

    def _check_cr(self, blue, red):
        try:
            if blue is not None:
                blue=self.gs.players[int(blue)]
            if red is not None:
                red=self.gs.players[int(red)]
            if not (blue or red):
                return 'give at least 1 player'
        except ValueError: return 'wrong data'
        return [blue, red]

    def cmwc_race(self, blue=None, red=None):
        players=self._check_cr(blue, red)
        if type(players)==str:
            return players
        elif not self.gs.race_is_runing:
            Race(self.gs, players)
            return "{0[name]} (blue) and {1[name]} (red)".format(players[0] or {'name':None},
                                                                 players[1] or {'name':None})
    def add_race(self, blue=None, red=None, b_set='_', r_set='_'):
        """add race to the queue (it will be started as soon as 'next_race' will be executed)"""
        msg=self._check_r(blue, red, b_set, r_set)
        if not msg:
            self.race_q.append((blue and {'name':blue, 'set':b_set},
                                red and {'name':red, 'set':r_set}))
            return 'added.'
        else:
            return msg

    def cmwc_add_race(self, blue=None, red=None):
        players=self._check_cr(blue, red)
        if type(players)==str:
            return players
        else:
            self.race_q.append(players)
            return 'added.'

    def next_race(self):
        if not self.gs.race_is_runing:
            racers=self.race_q.pop(0)
            Race(self.gs, racers)
            return '{0[name]} (blue) vs {1[name]} (red)'.format(*[ r or {'name':None} \
                                                                    for r in racers])
        else:
            return 'some race is actually running; wait a bit for its finish'

    def n_r(self):
        return self.next_race()

    @QtCore.Slot()
    def swap(self):
        if self.gs.race and not self.gs.race_is_runing:
            self.gs.race.swap_players()
            return '{0} (blue) vs {1} (red)'.format(*self.gs.race.player_names)
        else:
            return 'race is not established or is currently running'

    @QtCore.Slot()
    def start(self):
        if not self.gs.race_is_runing and self.gs.race:
            self.gs.race.start()
            return "3.. 2.. 1.. GO"
        else:
            return "the race is actually runing or hasnt been prepared yet"

    def s(self):
        return self.start()

    @QtCore.Slot()
    def abort(self):
        if self.gs.race and self.gs.race_is_runing:
            self.gs.abort.set()

        self.gs.out.abort()
        return 'abort'

    def a(self):
        self.abort()

    @QtCore.Slot(str, result=str)
    def next_round(self, rset, vis=False):
        if rset in self.gs.sets and len(self.gs.finals_better[rset])>0:
            self.msg=self.gs.begin_round(rset, bool(int(vis)))
            return '\r\n'.join(self.msg)

    def n(self, *args, **kwargs):
        return self.next_round(*args, **kwargs)

    def print_msg(self):
        self.gs.vis.show(self.msg[1:], title=self.msg[0])

    def p(self):
        self.print_msg()

    def show_races(self, rset, vis=False):
        self.msg=self.gs.f_races_in_round(rset, int(vis))
        self.title='{0} races in round'.format(rset)

        return '\r\n'.join(self.msg)

    def sr(self, *args, **kwargs):
        return self.show_races(*args, **kwargs)

    def replace(self, rset, org, subst=None):
        msg=self.gs.f_replace(rset, org, subst)
        if msg=='ok':
            return self._res(self.gs.finals_better[rset], 'next round', enum=True)
        else: return msg

    def add(self, rset, pl):
        msg=self.gs.f_add(rset, pl)
        if msg=='ok':
            return self._res(self.gs.finals_better[rset], 'next round', enum=True)
        else: return msg

    @QtCore.Slot(str, str, int)
    def promote(self, rset, pl, pos=-1):
        msg=self.gs.f_promote(rset, pl, int(pos))
        if msg=='ok':
            return self._res(self.gs.finals_better[rset], 'next round', enum=True)
        else: return msg

    def cancel(self, rset, p1, p2):
        return self.gs.f_cancel_race(rset, (p1,p2))

    def clear_q(self):
        self.gs.times=[]

    @QtCore.Slot()
    def sponsors(self):
        self.gs.out.sponsors()
        return 'ok'

    @QtCore.Slot()
    def init_bt(self):
        if self.gs.dev.__class__ == BluetoothDev:
            self.gs.dev=BluetoothDev(self.gs.dev.name_str, self.gs.dev.treshold)
            return 'ok.'
        elif self.gs.dev.__class__ == DoubleBluetoothDev:
            self.gs.dev=DoubleBluetoothDev(self.gs.dev.name_str, self.gs.dev.treshold)
            return 'ok.'
        else:
            return 'nothing.'

    def clear_f(self):
        self.gs.final_results=[]

    @QtCore.Slot(str)
    def set_dist(self, d):
        if self.gs.race_is_runing:
            return "try when race will be finished or abort race first"
        else:
            try:
                self.gs.dist=int(d)
                self.gs.out.set_dist(int(d))
                return 'ok.'
            except ValueError:
                return 'wrong int data'

    def cmwc_add_participants(self, players_f):
        try:
            self.gs.players+=self.load_participants(open(players_f))
        except IOError, e:  return "I/O Error: {0}".format(e)
        return 'done.'

    @QtCore.Slot(str, str, result=str)
    def rename(self, src, dst):
        msg=''
        for p in reduce(lambda x,y: x+y, self.gs.finals_curr.values()): #reduce(lambda x,y: x+y, self.gs.finals_better.values())+\
            if p[1]['name']==src:
                p[1]['name']=dst
                msg+='changed in finals\r\n'
        if isinstance(self.gs, CMWCGoldsprints):
            if src.isdigit():
                try:
                    self.gs.players[int(src)]['name']=dst
                    msg+='changed in particiapant list'
                except IndexError: pass
            else:
                for p in self.gs.players:
                    if p and p['name']==src:
                        p['name']=dst
                        msg+='changed in participant list'
        return msg or 'nothing changed'

    def add_q_time(self, name, time):
        try:
            self.gs.times.append((int(time),name))
        except ValueError: return 'wrong int data'

    def del_q_times(self, name):
        for i,t in enumerate(self.gs.times):
            if t[1]==name: del(self.gs.times[i])

    def _res(self, table, header='RESULTS', enum=False):
        if table:
            msg='-'*8+header+'-'*8+'\r\n'
            for i,r in enumerate(table, 1):
                #print r
                if not r:
                    msg+='\r\n'
                    continue
                if enum:
                    msg+=('{0:>2}. {2[name]:15}'+\
                          (r[0] is None and ' '*4+'n/q' or '{1:>6.3f}')+'\r\n').format(i, *r)
                else:
                    msg+=('  {1[name]:15}'+(r[0] is None and ' '*4+'n/q' or '{0:>6.3f}')+'  \r\n').format(*r)
            msg+='='*25
            return msg
        else:
            return 'nothing.'

    @QtCore.Slot(str, int)
    def begin_finals(self, rset=None, n=8, show=False):
        try:
            n=int(n)
            if not n in (4,8,16,32):
                raise ValueError
        except ValueError:
            return 'wrong int data'

        if rset is None and any(map(len, self.gs.finals_results.values())):
            return """finals are actually running; try to restart the program\n and
            give the results file in the commandline"""
        elif rset in self.gs.sets and len(self.gs.finals_results[rset])>0:
            return """finals are actually running; try to restart the program\n and
            give the results file in the commandline"""
        if rset is None or rset in self.gs.sets:
            self.gs.choose_best(n, rset)
            return self.show_results(rset, n, show)
        else:
            return 'set not found'

    def show_times(self, rset=None, public=False):
        if rset is None:
            if public:
                for s in self.gs.sets:
                    self.gs.out.show_results(self.gs.times[s], '{0} times'.format(s.upper()),
                                             int(public)*1000)
            return '\r\n'.join([self._res(self.gs.times[s], '{0} TIMES'.format(s.upper())) \
                                for s in self.gs.sets])
        elif rset in self.gs.sets:
            if public: self.gs.out.show_results(self.gs.times[rset], '{0} times'.format(rset),
                                                int(public)*1000)
            return self._res(self.gs.times[rset], 'TIMES')
        else: return '{0} set isnt in current competition'.format(rset)

    @QtCore.Slot(str,int,int)
    def show_results(self, rset=None, n=0, public=False):
        #print self.gs.out.primary_vis.abort.is_set()
        try:
            n=int(n)
            public=int(public)
        except ValueError:
            return 'wrong int data'

        def ret_res(rset, n=n):
            if len(self.gs.best_times[rset])>0:
                t=self.gs.finals_results[rset]+self.gs.best_times[rset]
                if n>0: return t[:n]
                return t
            else:
                return self.gs._gen_bt(rset, n)

        if not rset:
            t=[]
            for s in self.gs.sets:
                t.append(ret_res(s))
                if public:
                    self.gs.out.show_results(t[-1], '{0} results'.format(s.upper(), public*1000))

            return '\r\n'.join([self._res(t[i], '{0} RESULTS'.format(s.upper()), enum=True) for i,s in \
                                          enumerate(self.gs.sets)])
        elif rset in self.gs.sets:
            t=ret_res(rset)
            if public:
                self.gs.out.show_results(t, '{0} results'.format(rset.upper()), public*1000)
            return self._res(t, '{0} RESULTS'.format(rset.upper()), enum=True)
        else:
            return '{0} set isnt in current competition'.format(rset)

    def quit(self):
        self.gs.abort.set()
        self.gs.quit.set()
        self.gs.out.quit()


class CommandServer(Thread):
    daemon=True

    def __init__(self,gs,port=9998, peers=None, daemon=True):
        Thread.__init__(self)

        self.name='CommandServer-0'
        print("setting up server")

        self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.gs=gs
        self.peers=peers
        self.daemon=daemon

        self.commands=Commands(self.gs)

        self.s.bind(('', port))
        self.s.listen(5)
        self.s.settimeout(10)

    def run(self):
        print("waiting for connections.. ")
        i=0
        while 1:
            try:
                clientsock, clientpeer = self.s.accept()
            except socket.timeout:
                if self.gs.quit.is_set():
                    self.s.close()
                    return
                continue
            f=clientsock.makefile('rw',1)
            if self.peers is not None and not clientpeer[0] in self.peers:
                f.write('youre not allowed\n')
                f.close()
                clientsock.close()
                return

            print("got connection from {0}".format(clientsock.getpeername()))
            self.gs.out.addcmd_sockf(f)
            i+=1
            t=Thread(target=self.handle, args=[f, clientsock],
                   name='CommandServer-{0}'.format(i))
            t.daemon=True
            t.start()

    def handle(self, f, clientsock):
        while 1:
            try:
                cmd=f.readline().strip()
                if cmd=='quit':
                    self.commands.quit()
                    break
                elif cmd.endswith('?'):
                    try:
                        cmd_func=getattr(self.commands, cmd[:-1])
                        cmd_args=getargspec(cmd_func)
                        if cmd_args.defaults:
                            args=' '.join(cmd_args.args[1:-len(cmd_args.defaults)]+\
                                          map(lambda a : '{0}={1}'.format(*a),
                                              zip(cmd_args.args[-len(cmd_args.defaults):],
                                                  cmd_args.defaults)))
                            f.write('{0} {1} -- {2}'.format(cmd[:-1], args, cmd_func.__doc__ or ''))
                        else:
                            f.write('{0} {1} -- {2}'.format(cmd[:-1],' '.join(cmd_args.args[1:]),
                                                           cmd_func.__doc__ or ''))
                    except AttributeError: f.write('command not found')
                elif cmd.find('(') < cmd.find(')'):
                    print cmd
                    f.write(eval('self.commands.{0}'.format(cmd)))
                else:
                    cmd=cmd.split()
                    if cmd and cmd[0] in dir(self.commands) and callable(getattr(self.commands, cmd[0])):
                        cmd_func=getattr(self.commands,cmd[0])
                        try:
                            if len(cmd)>1: f.write(cmd_func(*cmd[1:]))
                            else: f.write(cmd_func())
                        except Exception, e: f.write('command error: {0}'.format(e))
                    else:
                        f.write('command not found')
                f.write('\r\n')
            except socket.error, e:
                print(e)
                return

        clientsock.shutdown(socket.SHUT_RDWR)
        f.close()
        clientsock.close()


