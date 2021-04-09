#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
issue-todo

a program to help with juggling multiple
issues at once, giving quick access to their
GitLab issue pages. Goal is to significantly
reduce stress associated with having multiple
tasks to do by keeping track of what issues need
to be worked on in a concise list.

Author: Isaac
"""

try:
    from Tkinter import *
    from Tkinter import messagebox
    from Tkinter import ttk
except ImportError:
    from tkinter import *
    from tkinter import messagebox
    from tkinter import ttk

import os
import sys
import webbrowser

from dialogs import NewNamespaceDialog, NewIssueDialog
from models import Namespace, Issue
from storage import Storage

global EXIT_CBK
EXIT_CBK = []

# It's ok that this may not *always*
# happen, but it's nice to cleanup a bit
# when possible.
def reg_exit(handler):
    EXIT_CBK.append(handler)

def run_exit_handlers():
    for cbk in EXIT_CBK:
        cbk()

# namespace format:
# gitlab.url gitlabuser repository-name filekey

# namespace file format:
# 2 byte short specifying number of to-do entries
# for each entry:
#   2 byte short specifying the issue number
#   2 byte short specifying length of the description
#   n bytes representing a UTF-8 description string

class LockfileError(FileExistsError):
    def __init__(self, msg):
        FileExistsError.__init__(self, msg)
        
class IssueTodo(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        self.__root = args[0]
        self.__selected = None
        
        self.__build()
        self.__storageinit()

    def __storageinit(self):
        homedir = os.path.expanduser("~")
        basedir = os.path.join(homedir, '.issue-todo')
        self.__storage = Storage(basedir, reg_exit=reg_exit)

        # now init GUI
        nslist = self.__storage.namespaces
        names = []
        for ns in nslist:
            names.append(ns.getAsURL())
        self.__spaces.configure(values=names)

        if len(nslist) > 0:
            ns = nslist[0]
            self.select(ns)

    def __build(self):

        self.master.title("Issue To-do")
        self.master.minsize(500, 400)

        self.pack(fill=BOTH, expand=True)

        self.__toolbar = Frame(self, bd=1, relief='groove')
        self.__toolbar.columnconfigure(2, weight=1)
        
        self.__issues = Listbox(self)

        # config toolbar
        self.__add = Button(self.__toolbar, text="Add", command=self.__add_issue, state="disabled")
        self.__add.grid(column=0, row=0)

        self.__del = Button(self.__toolbar, text="Delete", command=self.__del_issue, state="disabled")
        self.__del.grid(column=1, row=0)

        self.__selected_ns = StringVar()
        self.__spaces = ttk.Combobox(self.__toolbar, textvariable=self.__selected_ns, state="readonly")
        self.__spaces.grid(column=2, row=0, sticky=(N, E, S, W))

        self.__spaces.bind('<<ComboboxSelected>>', self.__onselect)

        self.__add_ns = Button(self.__toolbar, text="Add Namespace", command=self.__add_ns)
        self.__add_ns.grid(column=3, row=0)

        self.__toolbar.pack(side=TOP, expand=0, fill=BOTH)
        self.__issues.pack(expand=1, fill=BOTH)

        self.__issues.bind('<Double-1>', self.__issue_dbl_click)

    def __issue_dbl_click(self, _):
        cissue = self.__storage.getIssues(self.__selected)[self.__issues.curselection()[0]]
        ns = self.__storage.getNamespaceByKey(self.__selected)
        issue_url = "%s/-/issues/%d" % (ns.getAsURL(protocol='https'), cissue.id)
        webbrowser.open_new_tab(issue_url)

    def __onselect(self, _):
        idx = self.__spaces.current()
        ns = self.__storage.namespaces[idx]
        self.select(ns)
        
    def select(self, ns):
        if self.__selected_ns.get() != ns.getAsURL():
            self.__spaces.set(ns.getAsURL())
            
        self.__selected = ns.key
        self.__add.configure(state=NORMAL)
        self.__del.configure(state=NORMAL)

        self.__issues.delete(0, END)
        issues = self.__storage.getIssues(ns.key)
        for issue in issues:
            self.__issues.insert(END, '#%d - %s' % (issue.id, issue.description))

    def __put_namespace(self, ns):
        self.__storage.addNamespace(ns)
        nslist = self.__storage.namespaces
        names = []
        for ns in nslist:
            names.append(ns.getAsURL())

        if self.__selected_ns.get() == '':
            self.select(ns)
            
        self.__spaces.configure(values=names)

    def __add_ns(self):
        nsdlg = NewNamespaceDialog(self, callback=self.__put_namespace)
        nsdlg.grab_set() # make dialog modal
        self.__root.wait_window(nsdlg)

    def __put_issue(self, iss):
        self.__storage.addIssue(self.__selected, iss)
        issues = self.__storage.getIssues(self.__selected)
        self.__issues.insert(END, ('#%d - %s') % (iss.id, iss.description))

    def __add_issue(self):
        nidlg = NewIssueDialog(self, callback=self.__put_issue)
        nidlg.grab_set()
        self.__root.wait_window(nidlg)

    def __del_issue(self):
        idx = self.__issues.curselection()[0]
        self.__issues.delete(idx)
        self.__storage.removeIssue(self.__selected, idx)

if __name__ == '__main__':
    try:
        root = Tk()
        app = IssueTodo(root)
        root.mainloop()
        run_exit_handlers()
    except LockfileError as e:
        messagebox.showerror("Error", "Data files are locked. Please be sure no other instance of this program is running.")
        sys.exit(1)
    except Exception as e:
        messagebox.showerror("Uncaught Error", str(e))
        sys.exit(1)
