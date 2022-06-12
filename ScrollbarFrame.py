# encoding: utf-8

from tkinter import *
from tkinter import ttk
import platform

class ScrollbarFrame(Frame):
    """
    Extends class tk.Frame to support a scrollable Frame
    This class is independent from the widgets to be scrolled and
    can be used to replace a standard tk.Frame
    """

    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.parent = parent
        # The Scrollbar, layout to the right
        self.vsb = ttk.Scrollbar(self, orient="vertical")
        self.vsb.pack(side="right", fill="y")

        # The Canvas which supports the Scrollbar Interface, layout to the left
        self.canvas = Canvas(self, bg="white")
        self.canvas.config(highlightthickness=0, borderwidth=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind the Scrollbar to the self.canvas Scrollbar Interface
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.configure(command=self.canvas.yview)

        # The Frame to be scrolled, layout into the canvas
        # All widgets to be scrolled have to use this Frame as parent
        self.scrolled_frame = Frame(self.canvas, background="white")
        self.canvas.create_window((4, 4), window=self.scrolled_frame, anchor="nw")

        # Configures the scrollregion of the Canvas dynamically
        self.scrolled_frame.bind("<Configure>", self.on_configure)

    def on_configure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        #self.canvas.configure(width=event.width, height=event.height, scrollregion=self.canvas.bbox("all"))
        h = self.parent.winfo_screenheight()
        if platform.system() == "Darwin":
            win_width, win_height = 1030, h*0.75
            self.canvas.configure(width=win_width, height=win_height, scrollregion=self.canvas.bbox("all"))
        elif platform.system() == "Linux":
            win_width, win_height = 1030, h * 0.75
            self.canvas.configure(width=win_width, height=win_height, scrollregion=self.canvas.bbox("all"))
        else:
            win_width, win_height = 820, h*0.8
            self.canvas.configure(width=win_width, height=win_height, scrollregion=self.canvas.bbox("all"))

    def scroll_to(self, pos):
        self.canvas.yview_moveto(pos)