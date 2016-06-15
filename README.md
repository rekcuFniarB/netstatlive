Netstat Live
============

About
-----

Netstat Live is a graphical network connections monitor grouping by process names. Based on [this module](https://github.com/da667/netstat).

Not all processes can be identified, non-owned process info  will not be shown, you would have to run as root to see it all.

This project uses git submodule with 3rd party project. After clonning run `git submodule init` and `git submodule update` commands.

Requirements
------------

* python 2.7
* [netstat module](https://github.com/da667/netstat)
* tkinter (debian: python-tk)
* whois (optional)
* dig from dns-utils (optional, using for reverse lookup)
* xclip (optional, using for copying remote address)

Screenshots
-----------

![Screenshot: main window](http://i.imgur.com/lLHW8hf.png "Screenshot: main window")

![Screenshot: context menu](http://i.imgur.com/xMpgnRO.png "Screenshot: context-menu")

![Screenshot: whois popup](http://i.imgur.com/xi9Z970.png "Screenshot: whois pupup")
