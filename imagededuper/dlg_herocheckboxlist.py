import tkinter
# from tkinter import *
from PIL import Image, ImageTk
from tkinter import simpledialog
import ipdb  # noqa


class HeroCheckboxList(simpledialog.Dialog):
    data = []
    suggested = None
    result = None
    __image = None
    mtitle = None
    listbox = None

    def __init__(self, parent, title=None):
        if parent is None:
            self.mparent = tkinter.Tk()
        else:
            self.mparent = parent

    def window_init(self):
        tkinter.Toplevel.__init__(self, self.mparent)

        if self.mtitle:
            self.title(self.mtitle)

        self.parent = self.mparent

        upper_frame = tkinter.Frame(self)
        # START FRAME_IN_CANVAS
        self.canvas = tkinter.Canvas(upper_frame, borderwidth=0,
            background="#ffffff")
        self.frame = tkinter.Frame(self.canvas, background="#ffffff")
        self.vsb = tkinter.Scrollbar(upper_frame, orient="vertical",
            command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.OnFrameConfigure)

        # END FRAME_IN_CANVAS
        body = self.frame
        self.initial_focus = self.body(body)

        self.buttonbox()

        self.grab_set()

        upper_frame.pack(expand=True, fill="both")
        self.button_box.pack()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        screen_height = self.parent.winfo_screenheight()
        max_height = screen_height * 0.8
        self.update_idletasks()

        if self.frame.winfo_reqheight() > self.canvas.winfo_reqheight():
            requested_height = self.frame.winfo_reqheight() \
                + self.button_box.winfo_reqheight()
        else:
            requested_height = self.canvas.winfo_reqheight() \
                + self.button_box.winfo_reqheight()

        requested_width = self.frame.winfo_reqwidth() \
            + self.vsb.winfo_reqwidth()

        if requested_height > max_height:
            requested_height = max_height

        self.geometry("%dx%d%+d%+d" % (requested_width,
                                   requested_height,
                                   0,
                                   0))

        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master):
        self.result = None

        scrollbar = tkinter.Scrollbar(master, orient=tkinter.VERTICAL)

        self.listbox = listbox = tkinter.Listbox(master,
            yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tkinter.LEFT, fill=tkinter.Y)

        listbox.pack(side=tkinter.LEFT, fill=tkinter.Y)

        self.__image = ImageTk.PhotoImage(Image.open("%s"
            % self.data[0]['fullpath']))
        label = tkinter.Label(master, image=self.__image)
        label.pack()

        for item in self.data:
            listbox.insert(tkinter.END, item['name'])
            if item['suggest']:
                print('set suggest flag')
                listbox.select_set(listbox.size() - 1)

    def apply(self):
        self.result = self.listbox.curselection()

    def set_data(self, data):
        self.data = data

    def OnFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def buttonbox(self):
        self.button_box = tkinter.Frame(self)

        w = tkinter.Button(self.button_box, text="OK", width=10,
            command=self.ok, default=tkinter.ACTIVE)
        w.pack(side=tkinter.LEFT, padx=5, pady=5)
        w = tkinter.Button(self.button_box, text="Cancel", width=10,
            command=self.cancel)
        w.pack(side=tkinter.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
