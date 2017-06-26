import socket
import mmap
from subprocess import Popen, PIPE
from threading import Thread


class Dev:
    def __init__(self, name_str='', threshold=40):
        self.name_str=name_str
        self.threshold=threshold

    def clean(self):
        pass
    def check(self):
        pass
    def cycle(self):
        pass

class PygameDev(Dev):
    def __init__(self):
        import pygame

        self.pygame = pygame
        self. threshold = 1

    def cycle(self):
        ev = self.pygame.event.wait()

        if ev.type==self.pygame.KEYDOWN:
            if ev.key==self.pygame.K_LEFT:
                return 0
            elif ev.key == self.pygame.K_RIGHT:
                return 1
        return -1

class BluetoothDev(Dev):
    def __init__(self, name_str, threshold=40):
        print "bt_constructor", name_str
        Dev.__init__(self, name_str, threshold)
        import lightblue
        try:
            self.dev=lightblue.socket()
            self.dev.connect((name_str,1))
            self.dev.settimeout(0)
        except lightblue.BluetoothError:
            print('cant get bluetooth working')
            raise ValueError

    def clean(self):
        l=1
        while l>0:
            try: l=len(self.dev.recv(1024))
            except: l=0

    def check(self):
        try: l=self.dev.recv(100)
        except: l=0

        if l>self.threshold: return 'false start'

    def cycle(self):
        try:
            return int(self.dev.recv(1))
        except ValueError: return -2
        except socket.error, e:
            if e.message.find('11') >=0: return -1
            else:
                print(e.message)
                return -2


class DoubleBluetoothDev(Dev):
    def __init__(self, name_str, threshold=40):
        Dev.__init__(self, name_str, threshold)
        import lightblue
        try:
            name_str=name_str.partition(',')
            dev_l=[ d[0] for d in lightblue.finddevices() ]
            print dev_l
            if name_str[0] in dev_l and name_str[2] in dev_l:
                self.dev=[lightblue.socket(), lightblue.socket()]
                self.dev[0].connect((name_str[0],1))
                self.dev[0].settimeout(0)
                self.dev[1].connect((name_str[2],1))
                self.dev[1].settimeout(0)
            else:
                raise lightblue.BluetoothError
        except lightblue.BluetoothError:
            print('cant get bluetooth working')
            raise ValueError

    def clean(self):
        l1=1
        l2=1
        while l1>0 or l2>0:
            try: l1=len(self.dev[0].recv(1024))
            except: l1=0
            try: l2=len(self.dev[1].recv(1024))
            except: l2=0

    def check(self):
        self.curr=0
        try: l1=len(self.dev[0].recv(100))
        except: l1=0
        try: l2=len(self.dev[1].recv(100))
        except: l2=0

        if l1>self.threshold or l2>self.threshold:
            return 'false start'

    def cycle(self):
        curr=self.curr
        self.curr=int(not self.curr)
        try:
            self.dev[curr].recv(1)
            return curr
        except socket.error: return -1


class DoubleSerialDev(Dev):
    def __init__(self, name_str, threshold=40):
        Dev.__init__(self,name_str, threshold)
        import serial
        try:
            names = name_str.partition(',')
            self.dev = [ serial.Serial(names[0], 115200, timeout=0),
                         serial.Serial(names[2], 115200, timeout=0) ]
        except serial.serialutil.SerialException:
            print('cant connect to any serial ports')
            raise ValueError

    def clean(self):
        self.dev[0].readall()
        self.dev[1].readall()

    def check(self):
        self.curr=0
        if len(self.dev[0].read(100))>self.threshold or len(self.dev[1].read(100))>self.threshold:
            return 'false start'

    def cycle(self):
        curr=self.curr
        self.curr=int(not self.curr)
        if self.dev[curr].read(1):
            return curr
        else:
            return -1

    def cycle2(self, n):
        if self.dev[n].read(1):
            return n
        return -1


class SerialDev(Dev):
    def __init__(self, name_str, threshold=40):
        Dev.__init__(self,name_str, threshold)
        import serial
        self.serial = serial
        try:
            self.dev = serial.Serial(name_str, 115200, timeout=0.1)
        except serial.serialutil.SerialException:
            print('cant connect to serial port')
            raise ValueError
        self.sig = [0, 0]

    def clean(self):
        self.dev.readall()

    def check(self):
        if len(self.dev.readall())>self.threshold*5:
            return 'false start'

    def cycle(self):
        try:
            ret = int(self.dev.read(1))
            self.sig[ret]+=1
            if self.sig[ret]>=self.threshold:
                self.sig[ret]-=self.threshold
                return ret
        except ValueError: return -1
        return -1


class SerialReader(Dev):
    def __init__(self, name_str, threshold=5):
        import serial
        self.serial = serial
        try:
            self.dev = serial.Serial(name_str, 115200, timeout=0)
        except serial.serialutil.SerialException:
            print('cant connect to serial port')
            raise ValueError

        self.threshold = threshold
        self.sig = [0,0]

    def clean(self):
        self.dev.write('C')
        self.dev.readall()
        self.sig = [0,0]

    def check(self):
        row = self.dev.readall().rpartition(')')[0].rpartition('(')[2].split(' ')
        if len(row)==2 and any([ int(n)>5*self.threshold for n in row ]):
            return 'false start'

    def dist(self, player):
        row = self.dev.readall().rpartition(')')[0].rpartition('(')[2].split(' ')
        if len(row)==2 and row[0].isdigit() and row[1].isdigit():
            self.sig = map(int, row)

        return self.sig[player]


class RaspGPIODev(Dev, Thread):
    def __init__(self, config, threshold=5):
        import RPi.GPIO as GPIO
        self.GPIO = GPIO
        Thread.__init__(self)
        GPIO.setmode(GPIO.BOARD)
        blue, colon, red = config.partition(',')
        self.blue_pin = int(blue[:-1])
        self.red_pin = int(red[:-1])

        if blue[-1]=='U':
            GPIO.setup(self.blue_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.blue_pull=True
        else:
            GPIO.setup(self.blue_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self.blue_pull=False

        if red[-1]=='U':
            GPIO.setup(self.red_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.red_pull=True
        else:
            GPIO.setup(self.red_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self.red_pull=False

        self.blue_sig = 0
        self.red_sig = 0
        self.threshold = threshold

    def run(self):
        blue_old = 1 if self.blue_pull else 0
        red_old = 1 if self.red_pull else 0
        while True:
            blue_new = self.GPIO.input(self.blue_pin)
            red_new = self.GPIO.input(self.red_pin)
            if blue_new != blue_old:
                self.blue_sig+=1
                blue_old=blue_new
            if red_new != red_old:
                self.red_sig += 1
                red_old = red_new

    def clean(self):
        self.blue_sig=0
        self.red_sig=0
        if not self.is_alive():
            self.start()

    def check(self):
        if self.blue_sig>self.threshold*5:
            return 'false start'
        if self.red_sig>self.threshold*5:
            return 'false start'

    def cycle(self):
        if self.blue_sig>=self.threshold:
            self.blue_sig-=self.threshold
            return 0
        if self.red_sig>=self.threshold:
            self.red_sig-=self.threshold
            return 1
        return -1


class ShmReader(Dev):
    def __init__(self, config, threshold=5, false_start=5, blue_shmem_name="/blue.shmem",
                 red_shmem_name="/red.shmem", clear_sem_name="/clear.sem",
                 mem=4096):
        import posix_ipc as ipc
        self.ipc = ipc
        self.threshold = threshold
        self.false_start = false_start
        self.mem = mem

        self.blue_shmem = ipc.SharedMemory(blue_shmem_name, ipc.O_CREAT,
                                           mode=0666, size=self.mem)
                                           #read_only=True)
        self.red_shmem = ipc.SharedMemory(red_shmem_name, ipc.O_CREAT,
                                          mode=0666, size=self.mem)
                                          #read_only=True)
        self.clear_sem = ipc.Semaphore(clear_sem_name, ipc.O_CREAT, 0666, 0)

        self.red_map = mmap.mmap(self.red_shmem.fd, self.mem, mmap.MAP_SHARED,
                                 mmap.PROT_READ)
        self.blue_map = mmap.mmap(self.blue_shmem.fd, self.mem, mmap.MAP_SHARED,
                                  mmap.PROT_READ)

        # spawning C program that handles gpio signals
        Popen(['', '/home/koral/goldio/goldwire', config, str(threshold), str(mem)],
              executable='/usr/bin/sudo',
              stdout=PIPE)

    def clean(self):
        self.clear_sem.release()

    def _get_dist(self, f):
        f.seek(0)
        val = f.read(self.mem).replace('\x00', '')
        if len(val):
            return int(val)
        else:
            return -1

    def check(self):
        if self._get_dist(self.red_map)>=self.false_start:
            return 'false start'
        if self._get_dist(self.blue_map)>=self.false_start:
            return 'false start'

    def dist(self, player):
        if player==0:
            return self._get_dist(self.blue_map)
        else:
            return self._get_dist(self.red_map)
