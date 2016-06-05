Netstat Live
============

About
-----

Netstat Live is a graphical network connections monitor grouping by processes based on [this module](https://github.com/da667/netstat).

Not all processes can be identified, non-owned process info  will not be shown, you would have to run as root to see it all.

This project uses git submodule with 3rd party project. After clonning run `git submodule init` and `git submodule update` commands.

Requirements
------------

* python 2.7
* [netstat module](https://github.com/da667/netstat)
* tkinter (debian: python-tk)
* whois (optional)
* dns-utils (optional, using for reverse lookup)

Bulds
-----

[Deb package](http://brainfucker.myihor.ru/share/apps/netstatlive/builds/netstatlive_0.1-2_all.deb) (Ubuntu, Debian)

Screenshots
-----------

![Screenshot: main window](http://i.imgur.com/lLHW8hf.png "Screenshot: main window")

![Screenshot: context menu](http://i.imgur.com/H6oDCAD.png "Screenshot: context-menu")

![Screenshot: whois popup](http://i.imgur.com/xi9Z970.png "Screenshot: whois pupup")
