try:
    from Tkinter import *
    from Tkinter import messagebox
except ImportError:
    from tkinter import *
    from tkinter import messagebox

from models import Namespace, Issue
import re

class NewNamespaceDialog(Toplevel):
    def __init__(self, parent, callback=None):
        Toplevel.__init__(self, parent)
        self.__build()
        self.__cbk = callback

    def __build(self):
        self.columnconfigure(1, weight=1)
        
        baseurl_lbl = Label(self, text="Base URL:", anchor=E)
        gitlab_user_lbl = Label(self, text="Repository Owner:", anchor=E)
        gitlab_repo_lbl = Label(self, text="Repository Name:", anchor=E)

        self.__bu = StringVar()
        self.__gu = StringVar()
        self.__re = StringVar()

        baseurl = Entry(self, textvariable=self.__bu)
        gitlab_user = Entry(self, textvariable=self.__gu)
        gitlab_repo = Entry(self, textvariable=self.__re)

        baseurl_lbl.grid(column=0, row=0, sticky=(N, E, S, W))
        baseurl.grid(column=1, row=0)

        gitlab_user_lbl.grid(column=0, row=1, sticky=(N, E, S, W))
        gitlab_user.grid(column=1, row=1)

        gitlab_repo_lbl.grid(column=0, row=2, sticky=(N, E, S, W))
        gitlab_repo.grid(column=1, row=2)

        gitlab_repo.bind('<Return>', self._ok)

        ok = Button(self, text="OK", command=self._ok)
        ok.grid(column=1, row=3, sticky=(N, E, S, W))

    def _ok(self, _=None):
        if not re.search('^[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)+$', self.__bu.get()):
            messagebox.showerror("Invalid Namespace", "Please enter a valid base URL (do NOT include protocol - i.e. http://)")
            return
        if not re.search('^[a-zA-Z0-9_\-]+$', self.__gu.get()):
            messagebox.showerror("Invalid Namespace", "Please enter a simple GitLab username (alphanumeric, can includes underscore/hyphen)")
            return
        if not re.search('^[a-zA-Z0-9_\-]+$', self.__re.get()):
            messagebox.showerror("Invalid Namespace", "Please enter a simple GitLab repository name (alphanumeric, can includes underscore/hyphen)")
            return
        if self.__cbk is not None:
            self.__cbk(Namespace(self.__bu.get(), self.__gu.get(), self.__re.get(), str(uuid.uuid4())))
        self.destroy()

class NewIssueDialog(Toplevel):
    def __init__(self, parent, callback=None):
        Toplevel.__init__(self, parent)
        self.__cbk = callback
        self.__build()

    def __build(self):
        issue_num_lbl = Label(self, text="Issue #", anchor=E)
        description_lbl = Label(self, text="Description", anchor=E)

        self.__iss = StringVar()
        self.__desc = StringVar()
        
        issue_num = Spinbox(self, from_=1, to=10000, textvariable=self.__iss)
        description = Entry(self, textvariable=self.__desc)

        issue_num_lbl.grid(column=0, row=0, sticky=(N, E, S, W))
        issue_num.grid(column=1, row=0)

        description_lbl.grid(column=0, row=1, sticky=(N, E, S, W))
        description.grid(column=1, row=1, sticky=(N, E, S, W))

        description.bind('<Return>', self._ok)

        ok = Button(self, text="OK", command=self._ok)
        ok.grid(column=1, row=2, sticky=(N, E, S, W))

    def _ok(self, _=None):
        f = None
        try:
            f = int(self.__iss.get())
        except ValueError:
            messagebox.showerror("Invalid Issue", "Please input a valid issue number.")
            return

        if callable(self.__cbk):
            self.__cbk(Issue(f, self.__desc.get()))

        self.destroy()
