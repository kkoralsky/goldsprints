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

Whole system hopefully is platform independent. At least it runs on
Linux and probably on Windows XP.

- Python >= 2.6
- Pygame >= 1.9
- QT4, QML


Installation
============

# Install required packages. In Debian/Ubuntu:

    # apt-get install libqt4-dev qt4-qmake build-essential python-pygame

# install python modules (from main directory)

    $ pip install -r requirements

I recommend to create proper [virtual environment](https://virtualenv.pypa.io/en/latest/)
first though and then, run `pip`.


Quick start
===========

Type:

    ./main --help 

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
network. Basically, you need to connect to port 9998 to host running ./main.py
is installed. To see commands you can use type: `help`


Hacking
=======

Files
-----
- main.py - main program which handles commandline options,
  	    starts 2 frontends (command server - cmdserver.py and 
	    graphical one - pgfrontend.py) to control competition
- client.py - graphical frontend to start and abort races
- goldsprints.py - main goldpsprints engine in charge of taking data
  		   from arduino, writing times and figuring out next
		   race according to single-elimination tournament
- visualize.py - classes controlling graphical output; pygame based
- child.py - another instance of program which takes data by pipe from 
  	     main.py and visualize them on window (also using pygame
	     library)
- cmdserver.py - network server accepting commands from raw telnet
  	       	 client
- pgfrontend.py - graphical client intended to work locally
    (unlike client.py)
