# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from Lesson import Lesson



class ChangeDayDialog(object):

    BUTTON_OK = 1
    BUTTON_CANCEL = -1
    BUTTON_RESTORE = 0

    def __init__(self, parent, message):
        """
        Upon __init__ asks the user to change one or all day labels.
        Usage:
            dia = ChangeDayDialog(parent, message)
            parent.wait_window(dia.top)
            new_day, change = dia.day, dia.change_all
        """

        self.day = ""
        self.change_all = False
        self.result = -1


        top = self.top = tk.Toplevel(parent)
        top.withdraw()
        top.attributes('-alpha', 0)

        self.bg_strip = ttk.Frame(top)
        top_strip = ttk.Frame(self.bg_strip)
        button_strip = ttk.Frame(self.bg_strip)

        self.label_info = ttk.Label(top_strip, text=message)
        self.label_info.grid(row=0, column=0, pady=10, sticky="W")

        self.var_day = tk.StringVar(top_strip)
        self.entry_day = ttk.Entry(top_strip, width=22, textvariable=self.var_day)
        self.entry_day.grid(row=1, column=0, sticky="W")

        self.var_all = tk.BooleanVar(top_strip)
        self.checkbox_all = ttk.Checkbutton(top_strip, text="Ändra alla", variable=self.var_all, command=self.all_pressed)
        self.checkbox_all.grid(row=2, column=0, sticky="W", pady=10)

        self.button_cancel = ttk.Button(button_strip, text="Avbryt", command=self.cancel_pressed)
        self.button_cancel.grid(row=0, column=2, padx=5)

        self.button_restore = ttk.Button(button_strip, text="Återställ", command=self.restore_pressed)
        self.button_restore.grid(row=0, column=1, padx=5)

        self.button_ok = ttk.Button(button_strip, text="Ändra", command=self.ok_pressed)
        self.button_ok.grid(row=0, column=0, padx=5)

        top_strip.grid(row=0, column=0, pady=5, padx=10, sticky=tk.N+tk.E+tk.W)
        button_strip.grid(row=1, column=0, padx=10, pady=15, sticky=tk.E)

        self.bg_strip.grid(row=0, column=0, sticky=tk.NSEW)
        top.bind("<Return>", self.return_pressed)
        top.bind("<Key-Escape>", self.esc_pressed)

        # center the window
        #top.update()
        top.update_idletasks()
        w = top.winfo_reqwidth()
        h = top.winfo_reqheight()
        ws = top.winfo_screenwidth()
        hs = top.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        top.geometry('+%d+%d' % (x, y))

        top.resizable(False, False)
        self.entry_day.focus_set()
        top.attributes('-alpha', 1)
        top.deiconify()


    def all_pressed(self):
        self.change_all = self.var_all.get()

    def return_pressed(self, event):
        self.ok_pressed()

    def esc_pressed(self, event):
        self.cancel_pressed()

    def ok_pressed(self):
        # check if days are ok, warn if not
        inv_days = Lesson.get_invalid_days([self.var_day.get()])
        if inv_days:
            tk.messagebox.showwarning(master=self.top,
                                      title="Fel", message="Följande dag(ar) är inte gilitga:\n" + " ".join(inv_days))
            return

        self.result = ChangeDayDialog.BUTTON_OK
        self.day = self.var_day.get()
        self.change_all = self.var_all.get()
        self.top.destroy()

    def cancel_pressed(self):
        self.result = ChangeDayDialog.BUTTON_CANCEL
        self.top.destroy()

    def restore_pressed(self):
        self.result = ChangeDayDialog.BUTTON_RESTORE
        self.top.destroy()


if __name__ == "__main__":
    def on_click():
        dia = ChangeDayDialog(root, "Ändra från onsdag till:")
        root.wait_window(dia.top)
        
        if dia.result == ChangeDayDialog.BUTTON_CANCEL:
            print("Användaren avbröt")
        elif dia.result == ChangeDayDialog.BUTTON_RESTORE:
            print("Återställer")
        else:
            print("Ändrar dag till", dia.day)
            print("Ändrar alla:", dia.change_all)
    
    root = tk.Tk()
    mainLabel = tk.Label(root, text='Example for pop up input box')
    mainLabel.grid(row=0, column=0)

    mainButton = tk.Button(root, text='Click me', command=on_click)
    mainButton.grid()

    root.mainloop()
