This is software for [Goldsprint competitions](http://en.wikipedia.org/wiki/Goldsprint).


Requirements
============

Hardware
--------

Either:
- Arduino board
- Raspberry Pi 

Backend part is dumb simple and can be easily ported to other platforms.

Beyond that:
- Optionally Nokia N900 for controlling competition remotely
- TV flat screen or projector for visualization would be useful.


Software
--------

Since whole application is wrtitten in Python using Pygame and QT4 it should be
runnable on Windows, MacOS X and Linux. The only platform it was really tested,
though was Linux. Below are basic system requirements:

- Python >= 2.6
- Pygame >= 1.9
- QT4, QML


Installation
============

1. Install required packages.

   In Debian/Ubuntu Linux:

        $ sudo apt-get install libqt4-dev qt4-qmake build-essential python-pygame\
                libopenobex2-dev cmake libpyside1.2

2. install python modules (from main directory)

        $ pip install -r requirements

   I recommend to create proper [virtual environment](https://virtualenv.pypa.io/en/latest/)
   first though and then, run `pip`.


Quick start
===========

Type:

    python gold.py --help 

to see how to run program. 

Visualizations
--------------

You can have maximum 3 independent visualization of competion, but currently
there are only 2 different options to choose from:

- simple bars 
- paralax 2d game like animation

Typically, you set bars visualization for contenders and game-like visualization
for publicity.

Remote control via telnet
-------------------------

It's possible to control the competition via remote computer over
network. Basically, you need to connect to port 9998 to host running `gold.py`
is installed. To see commands you can use type: `help`


Hacking
=======

Files
-----
- `gold.py ` - main program which handles commandline options;
  starts 2 control interfaces (command server - `src/cmdserver.py`
  and graphical one - either based on pygame: `src/pgfrontend.py`
  or QT4 & QML: `src/qtcontrol.py` & `qml/view_n900.qml`)
- `src/qtclient.py` - graphical frontend to remotely control races via network
- `src/goldsprints.py` - main goldpsprints engine in charge of taking data from
  input device (arduino or raspberry pi), writing times etc.
- `src/visualize.py` - classes controlling graphical output; pygame based
- `src/device.py` - input device drivers
- `remote_child.py` - another instance of program which takes data by pipe from 
  main.py and visualize them on window (also using pygame library)
