# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk


class ChangeInfoDialog(object):
    def __init__(self, parent, message="Ändra kursansvarig och/eller skola."):
        """
        Upon __init__ asks the user what week and day to place the lesson to be created.
        Usage:
        dia = ChangeInfoDialog(parent, message)
        parent.wait_window(dia.top)
        name, group = dia.name, dia.group
        """

        self.teacher = ""
        self.school = ""
        self.cancelled = True

        top = self.top = tk.Toplevel(parent)
        top.title("Ändra info")
        top.withdraw()
        top.attributes('-alpha', 0)

        self.bg_strip = ttk.Frame(master=top)
        self.bg_strip.grid(row=0, column=0, sticky="nsew")

        self.top_strip = ttk.Frame(master=self.bg_strip)
        self.button_strip = ttk.Frame(master=self.bg_strip)

        self.label_info = ttk.Label(self.top_strip, text=message)
        self.label_info.grid(row=0, column=0, pady=10, padx=5, columnspan=2, sticky="W")

        ttk.Label(self.top_strip, text="Kursansvarig: ").grid(row=1, column=0, padx=(5,0), sticky="E")
        self.var_teacher = tk.StringVar(top)
        self.entry_teacher = ttk.Entry(self.top_strip, width=30, textvariable=self.var_teacher)
        self.entry_teacher.grid(row=1, column=1, padx=5)
        self.var_teacher.set(parent.subject.teacher)

        ttk.Label(self.top_strip, text="Skola: ").grid(row=2, column=0, padx=(5,0), sticky="E")
        self.var_school = tk.StringVar(self.top_strip)
        self.entry_school = ttk.Entry(self.top_strip, width=30, textvariable=self.var_school)
        self.entry_school.grid(row=2, column=1, padx=5, pady=(5,0))
        self.var_school.set(parent.subject.school)

        self.button_ok = ttk.Button(self.button_strip, text="OK", width=10, command=self.ok_pressed)
        self.button_ok.grid(row=3, column=0, pady=10, padx=5, sticky="E")

        self.button_cancel = ttk.Button(self.button_strip, text="Avbryt", width=10, command=self.cancel_pressed)
        self.button_cancel.grid(row=3, column=1, pady=10, padx=5)

        self.top_strip.grid(row=0, column=0, pady=(5, 5))
        self.button_strip.grid(row=1, column=0, pady=(10, 5))

        top.bind("<Return>", self.return_pressed)
        top.bind("<Key-Escape>", self.esc_pressed)

        # center the window
        # top.update()
        top.update_idletasks()
        w = top.winfo_reqwidth()
        h = top.winfo_reqheight()
        ws = top.winfo_screenwidth()
        hs = top.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        top.geometry('+%d+%d' % (x, y))

        top.resizable(False, False)
        self.entry_teacher.icursor(tk.END)
        self.entry_school.icursor(tk.END)
        self.entry_teacher.focus_set()
        top.attributes('-alpha', 1)
        top.deiconify()

    def return_pressed(self, event):
        self.ok_pressed()

    def esc_pressed(self, event):
        self.cancel_pressed()

    def ok_pressed(self):
        # check if days are ok, warn if not

        self.cancelled = False
        self.teacher = self.var_teacher.get()
        self.school = self.var_school.get()
        self.top.destroy()

    def cancel_pressed(self):
        self.top.destroy()


if __name__ == "__main__":
    def on_click():
        dia = ChangeInfoDialog(root, "Skapa ny lektion")
        root.wait_window(dia.top)

        if dia.cancelled:
            print("Användaren avbröt")
        else:
            print("Ny titel:", dia.teacher + " vid " + dia.school)


    root = tk.Tk()
    mainLabel = tk.Label(root, text='Example for pop up input box')
    mainLabel.grid(row=0, column=0)

    mainButton = tk.Button(root, text='Click me', command=on_click)
    mainButton.grid()

    root.mainloop()
