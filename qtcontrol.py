from threading import Thread

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtDeclarative import QDeclarativeView
import csv

from cmdserver import Commands

class OutInterface(QObject):
    update_race=Signal(int,int,float,float,float)
    abort=Signal()
    finish=Signal(float,float)
    start=Signal()
    new_race=Signal(unicode, unicode)

class ResultsModel(QAbstractListModel):
    NAME_ROLE = Qt.UserRole+1
    RES_ROLE = Qt.UserRole+2

    def __init__(self, results):
        QAbstractListModel.__init__(self, None)
        self.results=results
        self.setRoleNames({ ResultsModel.NAME_ROLE : 'name', ResultsModel.RES_ROLE : 'result' })

    def data(self, index, role):
        if role == ResultsModel.NAME_ROLE:
            return self.results[index.row()][1]['name']
        elif role == ResultsModel.RES_ROLE:
            return self.results[index.row()][0]

    def rowCount(self, index):
        return len(self.results)


class QtControl(Thread):
    def __init__(self, gs):
        super(QtControl, self).__init__()

        self.gs = gs
        self.cmd=Commands(gs)
        self.results=ResultsModel(self.gs.best_times['_'])

    def get_results(self):
        # self.ctxt.setContextProperty("resutlts", [['<b>{0: >4}.</b> {2} [<font align="right" color="grey">{1:.2f}</font>]'.format(i, t[0], t[1]['name'])
        #                                               for i,t in enumerate(self.gs.best_times[s],1)]
        #                                              for s in self.gs.sets])
        self.ctxt.setContextProperty("results", self.results)

    def run(self):
        self.app=QApplication([])
        self.view=QDeclarativeView()
        self.view.setResizeMode(QDeclarativeView.SizeRootObjectToView)


        self.ctxt = self.view.rootContext()
        # setting context properities
        self.ctxt.setContextProperty("sets", self.gs.sets)
        self.ctxt.setContextProperty("cmd", self.cmd)
        self.ctxt.setContextProperty("dist", self.gs.dist)
        self.ctxt.setContextProperty("results", self.results)

        self.view.setSource(QUrl('view_n900.qml'))
        self.root=self.view.rootObject()
        # connecting signals
        self.gs.out.qiface.update_race.connect(self.root.update_race)
        self.gs.out.qiface.start.connect(self.root.start)
        self.gs.out.qiface.abort.connect(self.root.abort)
        self.gs.out.qiface.finish.connect(self.root.finish)
        self.gs.out.qiface.finish.connect(self.get_results)
        self.gs.out.qiface.new_race.connect(self.root.new_race)

        self.view.show()
        self.app.exec_()

        #self.gs.out.quit()

if __name__ == "__main__":
    from goldsprints import Goldsprints, Output
    out=Output((640,480), 1, 5, 'bar', False, '', 'jakis_output.txt', 'jakies_finaly.pickle')
    gs=Goldsprints(out, 'faked_serial.txt', None, None, None, ['m','f'])

    for r in csv.reader(open('results.txt')):
        r=[ float(r[0]), dict(zip(('set', 'name'), r[1:])) ]
        if r[1]['set'] in gs.sets:
            gs.times[r[1]['set']].append(r)

    QtControl(gs).run()


