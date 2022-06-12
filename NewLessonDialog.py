# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from Lesson import Lesson


class NewLessonDialog(object):
	def __init__(self, parent, message):
		"""
		Upon __init__ asks the user what week and day to place the lesson to be created.
		Usage:
			dia = NewLessonDialog(parent, message)
			parent.wait_window(dia.top)
			day, week = dia.day, dia.week
		"""

		self.day = ""
		self.week = 0
		self.cancelled = True

		top = self.top = tk.Toplevel(parent)
		top.title("Ny lektion")
		top.withdraw()
		top.attributes('-alpha', 0)

		self.bg_strip = ttk.Frame(master=top)
		self.bg_strip.grid(row=0, column=0, sticky="nsew")

		self.top_strip = ttk.Frame(master=self.bg_strip)
		self.button_strip = ttk.Frame(master=self.bg_strip)

		self.label_info = ttk.Label(self.top_strip, text=message)
		self.label_info.grid(row=0, column=0, pady=5, padx=5, columnspan=2, sticky="W")

		ttk.Label(self.top_strip, text="Vecka: ").grid(row=1, column=0, sticky="E")
		self.var_week = tk.StringVar(top)
		self.entry_week = ttk.Entry(self.top_strip, width=10, textvariable=self.var_week)
		self.entry_week.grid(row=1, column=1, padx=5, pady=(0,2))

		ttk.Label(self.top_strip, text="Veckodag: ").grid(row=2, column=0, sticky="E")
		self.var_day = tk.StringVar(self.top_strip)
		self.entry_day = ttk.Entry(self.top_strip, width=10, textvariable=self.var_day)
		self.entry_day.grid(row=2, column=1, padx=5)

		self.button_ok = ttk.Button(self.button_strip, text="OK", width=10, command=self.ok_pressed)
		self.button_ok.grid(row=3, column=0, pady=10, padx=5, sticky="E")

		self.button_cancel = ttk.Button(self.button_strip, text="Avbryt", width=10, command=self.cancel_pressed)
		self.button_cancel.grid(row=3, column=1, pady=10, padx=5)

		self.top_strip.grid(row=0,column=0, pady=(5,5))
		self.button_strip.grid(row=1,column=0, pady=5, padx=(10,10))

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
		self.entry_week.focus_set()
		top.attributes('-alpha', 1)
		top.deiconify()

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
		self.cancelled = False
		self.day = self.var_day.get()

		try:
			self.week = int(self.var_week.get())
		except:
			tk.messagebox.showwarning(master=self.top, title="Fel",
									  message="Följande vecka är inte gilitg: " + self.var_week.get())
			return

		if self.week > 52 or self.week < 1:
			tk.messagebox.showwarning(master=self.top, title="Fel",
									  message="Följande vecka är inte gilitg: " + self.var_week.get())
			return

		self.top.destroy()

	def cancel_pressed(self):
		self.top.destroy()


if __name__ == "__main__":
	def on_click():
		dia = NewLessonDialog(root, "Skapa ny lektion")
		root.wait_window(dia.top)

		if dia.cancelled:
			print("Användaren avbröt")
		else:
			print("Ny lektion", dia.day + " vecka " + str(dia.week))


	root = tk.Tk()
	mainLabel = tk.Label(root, text='Example for pop up input box')
	mainLabel.grid(row=0, column=0)

	mainButton = tk.Button(root, text='Click me', command=on_click)
	mainButton.grid()

	root.mainloop()
