#!/usr/bin/python

from PySide.QtCore import Slot, QUrl, QObject, Signal
from threading import Thread
from time import sleep
from PySide.QtGui import *
from PySide.QtDeclarative import QDeclarativeView
import socket, sys
#from cmdserver import Commands

class QtClient:
    host="localhost"
    port=9998
    ctxt=''

    class Commands(QObject, Thread):
        finish = Signal()
        daemon = True

        def __init__(self, host, port):
            Thread.__init__(self)
            QObject.__init__(self)
            self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.connect((host,port))
            self.socket.settimeout(.5)
            self.setDaemon(True)

        def run(self):
            print 'running'
            while 1:
                try:
                    data = self.socket.recv(400)
                    if data:
                        print data
                    if data.startswith('finish'):
                        self.finish.emit()
                except socket.error:
                    sleep(3)
                except KeyboardInterrupt:
                    sys.exit()


        @Slot(str, str, str, str, result=str)
        def new_race(self, *args):
            self.socket.send('new_race("%s","%s","%s","%s")\n' % (args))

        @Slot()
        def swap(self):
            self.socket.send('swap\n')

        @Slot()
        def start_race(self):
            self.socket.send('start\n')

        @Slot()
        def abort(self):
            self.socket.send('abort\n')

        @Slot(str,int,int)
        def show_results(self, *args):
            try: self.socket.recv(4096)
            except socket.error: pass
            self.socket.send('show_results %s %s %s\n' % (args))
            results=''
            while 1:
                try: results+=self.socket.recv(4096)
                except socket.error: break
            results=results.splitlines()[1:-1]
            self.ctxt.setContextProperty('results', results)

        @Slot()
        def sponsors(self):
            self.socket.send("sponsors\n")

        @Slot()
        def init_bt(self):
            self.socket.send("init_bt\n")

        @Slot(str)
        def set_dist(self, *args):
            self.socket.send('set_dist("%s")\n' %(args))

    def __init__(self, host, port):
        self.host=host or self.host
        self.port=port or self.port

    def connect(self):
        self.cmd = self.Commands(self.host, self.port)
        self.cmd.start()

    def get_results(self):
        pass

    def show(self,qml_file):
        self.app=QApplication([])
        self.view=QDeclarativeView()
        self.view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        self.view.setSource(QUrl(qml_file))
        self.ctxt = self.view.rootContext()
        self.cmd.ctxt = self.ctxt
        self.ctxt.setContextProperty("cmd", self.cmd)
        self.cmd.finish.connect(self.view.rootObject().finish)
        #self.ctxt.setContextProperty("dist", self.cmd.abort())

        self.view.show()
        self.app.exec_()


if __name__ == "__main__":
    get_arg=lambda : len(sys.argv)>1 and sys.argv.pop(1) or None
    client=QtClient(host=get_arg(), port=get_arg())

    client.connect()
    client.show("view_n900.qml")



