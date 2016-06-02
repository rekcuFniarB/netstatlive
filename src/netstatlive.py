#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys, os
import Tkinter as tk
from ttk import Treeview, Scrollbar, Notebook
from time import sleep
from threading import Thread
from Queue import Queue

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lib', 'netstat'))
from netstat import netstat_tcp4, netstat_tcp6, netstat_udp4, netstat_udp6

class Application(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.title("Netstat Live")
        self.pack()
        
        master.protocol("WM_DELETE_WINDOW", self.app_quit)
        self._app_quit = False
        
        self._freeze = False
        
        self.tabs = Notebook(master)
        
        self.tabs_frames = {'TCP4': {'tab': None, 'tbl': None, 'query': netstat_tcp4},
                            'UDP4': {'tab': None, 'tbl': None, 'query': netstat_udp4},
                            'TCP6': {'tab': None, 'tbl': None, 'query': netstat_tcp6},
                            'UDP6': {'tab': None, 'tbl': None, 'query': netstat_udp6}
                           }
        for tab in self.tabs_frames:
            # Creating tabs
            self.tabs_frames[tab]['tab'] = tk.Frame(self.tabs)
            self.tabs.add(self.tabs_frames[tab]['tab'], text=tab)
            #self.tabs_frames[tab]['tab'].pack(fill=tk.BOTH)
            # Adding Treeview widget to tabs
            self.tabs_frames[tab]['tbl'] = Treeview(self.tabs_frames[tab]['tab'])
            self.tabs_frames[tab]['tbl']['columns'] = ('Pid', 'User', 'Local addr', 'Remote addr', 'State')
            for column in self.tabs_frames[tab]['tbl']['columns']:
                self.tabs_frames[tab]['tbl'].heading(column, text=column)
                self.tabs_frames[tab]['tbl'].column(column, width=150)
            self.tabs_frames[tab]['scrollbar_y'] = Scrollbar(self.tabs_frames[tab]['tab'], orient=tk.VERTICAL, command=self.tabs_frames[tab]['tbl'].yview)
            self.tabs_frames[tab]['tbl']['yscroll'] = self.tabs_frames[tab]['scrollbar_y'].set
            self.tabs_frames[tab]['scrollbar_y'].pack(side=tk.RIGHT, fill=tk.Y)
            self.tabs_frames[tab]['tbl'].pack(expand=tk.Y, fill=tk.BOTH)
        self.tabs.pack(fill=tk.BOTH, expand=tk.Y)
        
        # Freeze button
        self.buttons = tk.Frame(master)
        self.buttons.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.freeze_btn = tk.Button(self.buttons, text='Freeze', command=self.freeze_btn_handler)
        self.freeze_btn.pack(side=tk.RIGHT)
        
        self.queue = Queue(maxsize=1)
        self.poll = Thread(target=self.thread, args=(self.queue,))
        self.poll.start()
        
    def thread(self, queue):
        while not self._app_quit:
            if queue.empty():
                # Get netstat data
                netstat = self.tabs_frames[self.tabs.tab(self.tabs.select(), 'text')]['query']()
                # Put no queue
                queue.put(netstat, True)
            else:
                sleep(0.5)
    
    def app_quit(self):
        self._app_quit = True
        self.master.destroy()
    
    def refresh(self):
        if not self._freeze and not self.queue.empty():
            current_tab = self.tabs.tab(self.tabs.select(), 'text')
            # Get active tab
            tbl = self.tabs_frames[current_tab]['tbl']
            data = self.queue.get(False)
            processes = []
            for proc in data:
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
        
            for proc in data:
                proc_name = '%s (%s)' % (os.path.basename(str(proc[6])), str(proc[6]))
                #         Pid           User          Local addr    Remote addr   State
                values = (str(proc[5]), str(proc[1]), str(proc[2]), str(proc[3]), str(proc[4]))
                try:
                    tbl.insert(proc_name, 'end', text=proc_name, values=values)
                except:
                    pass
    
            # Removing empty root items
            for proc in tbl.get_children():
                if len(tbl.get_children(proc)) == 0:
                    tbl.delete(proc)
            
        self.master.after(500, self.refresh)
        
    def freeze_btn_handler(self):
        # Toggle freeze state
        if self._freeze:
            self.freeze_btn['text'] = 'Freeze'
        else:
            self.freeze_btn['text'] = 'Continue'
        self._freeze = not self._freeze

if __name__ == '__main__':
    app = Application(tk.Tk())
    app.master.after(10, app.refresh)
    app.master.mainloop()
