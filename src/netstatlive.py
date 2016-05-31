#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys, os
from Tkinter import *
from ttk import Treeview, Scrollbar
from time import sleep

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lib', 'netstat'))
from netstat import netstat_tcp4, netstat_tcp6, netstat_udp4, netstat_udp6

FREEZE = False
netstat = netstat_tcp4

def reset():
    for btn in proto_buttons:
        proto_buttons[btn]['state'] = 'normal'
    # Clear tree:
    tbl.delete(*tbl.get_children())

def freeze_btn_handler():
    global FREEZE
    if FREEZE:
        freeze_btn['text'] = 'Freeze'
    else:
        freeze_btn['text'] = 'Continue'
    FREEZE = not FREEZE

def tcp4_btn_handler():
    global netstat
    reset()
    proto_buttons['tcp4']['state'] = 'disabled'
    netstat = netstat_tcp4

def udp4_btn_handler():
    global netstat
    reset()
    proto_buttons['udp4']['state'] = 'disabled'
    netstat = netstat_udp4

def tcp6_btn_handler():
    global netstat
    reset()
    proto_buttons['tcp6']['state'] = 'disabled'
    netstat = netstat_tcp6

def udp6_btn_handler():
    global netstat
    reset()
    proto_buttons['udp6']['state'] = 'disabled'
    netstat = netstat_udp6

def refresh():
    global FREEZE
    if not FREEZE:
        lst = netstat()
        processes = []

        for proc in lst:
            processes.append(proc[6])
        processes = tuple(set(processes)) # Unique list of processes in netstat
        
        # Clear tree:
        for proc in tbl.get_children():
            tbl.delete(*tbl.get_children(proc))
    
        for proc in processes:
            proc_name = '%s (%s)' % (os.path.basename(str(proc)), str(proc))
            if not tbl.exists(proc_name):
                # Create root items for each process name
                tbl.insert('', 'end', proc_name, text=proc_name)
    
        for proc in lst:
            proc_name = '%s (%s)' % (os.path.basename(str(proc[6])), str(proc[6]))
            #         Pid           User          Local addr    Remote addr   State
            values = (str(proc[5]), str(proc[1]), str(proc[2]), str(proc[3]), str(proc[4]))
            tbl.insert(proc_name, 'end', text=proc_name, values=values)
        
        tbl.pack()
    root.after(50, refresh)

root = Tk()
root.title("Netstat Live")

main_frame = Frame(root)
main_frame.pack(expand=Y, fill=BOTH)

tbl = Treeview(main_frame)
tbl['columns'] = ('Pid', 'User', 'Local addr', 'Remote addr', 'State')
for column in tbl['columns']:
    tbl.heading(column, text=column)
    tbl.column(column, width=150)

scrollbar_y = Scrollbar(main_frame, orient=VERTICAL, command=tbl.yview)
tbl['yscroll'] = scrollbar_y.set
scrollbar_y.pack(side=RIGHT, fill=Y)

tbl.pack(expand=Y, fill=BOTH)

buttons_frame = Frame(root)
buttons_frame.pack(side=BOTTOM, fill=BOTH)

proto_buttons = {}
proto_buttons['tcp4'] = Button(buttons_frame, text='TCP4', state=DISABLED, command=tcp4_btn_handler)
proto_buttons['tcp4'].pack(side=LEFT)
proto_buttons['udp4'] = Button(buttons_frame, text='UDP4', command=udp4_btn_handler)
proto_buttons['udp4'].pack(side=LEFT)
proto_buttons['tcp6'] = Button(buttons_frame, text='TCP6', command=tcp6_btn_handler)
proto_buttons['tcp6'].pack(side=LEFT)
proto_buttons['udp6'] = Button(buttons_frame, text='UDP6', command=udp6_btn_handler)
proto_buttons['udp6'].pack(side=LEFT)

freeze_btn = Button(buttons_frame, text='Freeze', command=freeze_btn_handler)
freeze_btn.pack(side=LEFT)

root.after(10, refresh)

root.mainloop()
