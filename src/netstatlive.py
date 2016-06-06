#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Netstatlive - graphical network connections monitor grouping by processes
#    Copyright (C) 2016  BrainFucker <retratserif@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, subprocess
import Tkinter as tk
from ttk import Treeview, Scrollbar, Notebook
from time import sleep
from threading import Thread
from Queue import Queue
from collections import OrderedDict

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lib', 'netstat'))
from netstat import netstat_tcp4, netstat_tcp6, netstat_udp4, netstat_udp6

class Application(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.title("Netstat Live")
        self.pack(fill=tk.BOTH, expand=tk.Y)
        
        master.protocol("WM_DELETE_WINDOW", self.app_quit)
        self._app_quit = False
        
        self._freeze = False
        
        self.tabs = Notebook(self)
        
        self.tabs_frames = OrderedDict()
        self.tabs_frames['TCP4'] = {'query': netstat_tcp4}
        self.tabs_frames['UDP4'] = {'query': netstat_udp4}
        self.tabs_frames['TCP6'] = {'query': netstat_tcp6}
        self.tabs_frames['UDP6'] = {'query': netstat_udp6}
        
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
            # Bind right click event for displaying context menu
            self.tabs_frames[tab]['tbl'].bind('<Button-3>', self.context_menu_popup)
            self.tabs_frames[tab]['tbl'].bind('<Button-1>', self.context_menu_unpost)
        self.tabs.pack(fill=tk.BOTH, expand=tk.Y)
        
        # Freeze button
        self.buttons = tk.Frame(master)
        self.buttons.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.freeze_btn = tk.Button(self.buttons, text='Freeze', command=self.freeze_btn_handler)
        self.freeze_btn.pack(side=tk.RIGHT)
        
        # Check dependencies
        self._xclip = True
        self._whois = True
        try:
            out = subprocess.check_output(['xclip', '-h'], stderr=subprocess.STDOUT)
        except:
            self._xclip = False
        try:
            out = subprocess.check_output(['whois', '--version'], stderr=subprocess.STDOUT)
        except:
            self._whois = False
        
        # Connections list context menu
        self._remote_addr = ''
        self.context_menu = tk.Menu(self, tearoff=0)
        if self._xclip:
            self.context_menu.add_command(label='Copy remote addr.', command=self.xclip)
        if self._whois:
            self.context_menu.add_command(label='Whois', command=self.whois)
        self.tabs.bind('<Button-1>', self.context_menu_unpost)
        
        self.queue = Queue(maxsize=1)
        self.poll = Thread(target=self.thread, args=(self.queue,))
        self.poll.start()
        
    def context_menu_popup(self, event):
        tbl = self.get_active_tab()
        item = tbl.identify_row(event.y)
        if item and len(tbl.get_children(item)) == 0:
            tbl.selection_set(item)
            # Get remote addr value
            self._remote_addr = tbl.set(item, column='Remote addr')
            self.context_menu.post(event.x_root, event.y_root)
        else:
            # Mouse pointer is not over item
            pass
    
    def context_menu_unpost(self, event):
        self.context_menu.unpost()

    def get_active_tab(self):
        current_tab = self.tabs.tab(self.tabs.select(), 'text')
        tbl = self.tabs_frames[current_tab]['tbl']
        return tbl
    
    def thread(self, queue):
        while not self._app_quit:
            if queue.empty():
                # Get netstat data
                try:
                    netstat = self.tabs_frames[self.tabs.tab(self.tabs.select(), 'text')]['query']()
                except RuntimeError:
                    sys.stderr.write('Main thread destroyed.\n')
                # Put to queue
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
            
            # Remember focus
            self.tabs_frames[current_tab]['focus'] = tbl.selection()
            
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
                h = hash(tuple(proc))
                try:
                    tbl.insert(proc_name, 'end', h, text=proc_name, values=values)
                except:
                    pass
    
            # Removing empty root items
            for proc in tbl.get_children():
                if len(tbl.get_children(proc)) == 0:
                    tbl.delete(proc)
            
            # Restore focus
            try:
                tbl.selection_set(self.tabs_frames[current_tab]['focus'])
            except:
                pass
            
        self.master.after(500, self.refresh)
        
    def freeze_btn_handler(self):
        # Toggle freeze state
        if self._freeze:
            self.freeze_btn['text'] = 'Freeze'
        else:
            self.freeze_btn['text'] = 'Continue'
        self._freeze = not self._freeze

    def xclip(self, data=None):
        if not data:
            data = self._remote_addr
        try:
            xclip = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            xclip.communicate(input=data)
            xclip.terminate()
        except:
            pass
    
    def whois(self, addr=None):
        if not addr:
            addr = self._remote_addr
        addr = addr.split(':')
        try:
            reverse = subprocess.check_output(['dig', '+short', '-x', addr[0]])
        except:
            reverse = None
        
        try:
            out = subprocess.check_output(['whois', addr[0]])
        except:
            out = 'No info for this host.'
        
        self.whois_popup = {}
        self.whois_popup['window'] = tk.Toplevel(self)
        self.whois_popup['window'].title('Whois %s' % addr[0])
        self.whois_popup['frame'] = tk.Frame(self.whois_popup['window'])
        self.whois_popup['frame'].pack(fill=tk.BOTH, expand=tk.Y)
        self.whois_popup['text'] = tk.Text(self.whois_popup['frame'], wrap=tk.WORD, height=32, width=96)
        self.whois_popup['text'].pack(fill=tk.BOTH, expand=tk.Y, side=tk.LEFT)
        self.whois_popup['scrollbar_y'] = Scrollbar(self.whois_popup['frame'])
        self.whois_popup['scrollbar_y'].config(command=self.whois_popup['text'].yview)
        self.whois_popup['scrollbar_y'].pack(side=tk.RIGHT, fill=tk.Y)
        self.whois_popup['text'].config(yscrollcommand=self.whois_popup['scrollbar_y'].set)
        if reverse:
            reverse = 'Reverse lookup: %s\n' % reverse
            self.whois_popup['text'].insert(tk.END, reverse)
        self.whois_popup['text'].insert(tk.END, out)
            
        tk.Button(self.whois_popup['window'], text='Ok', command=self.whois_popup['window'].destroy).pack()

if __name__ == '__main__':
    app = Application(tk.Tk())
    app.master.after(10, app.refresh)
    try:
        app.master.mainloop()
    except KeyboardInterrupt:
        app.app_quit()
    except:
        raise
