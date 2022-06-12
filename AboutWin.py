# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk


class AboutWin(tk.Toplevel):

	def __init__(self, parent=None):
		super().__init__(master=parent)

		self.geometry("600x500")

		self.bg_frame = ttk.Frame(self)
		self.bg_frame.pack()

		self.text_area = tk.Text(master=self.bg_frame, font=(None, 12))
		self.text_area.pack(fill="y")

		self.protocol("WM_DELETE_WINDOW", self.on_close)

		self.fill_text()

		self.text_area.config(state=tk.DISABLED)

	def fill_text(self):
		with open("about.txt", "r", encoding="utf-8") as textf:
			while t := textf.readline():
				self.text_area.insert(tk.END, t)

	def on_close(self):
		self.destroy()


if __name__ == "__main__":
	def on_click():
		dia = AboutWin()
		dia.mainloop()


	root = tk.Tk()
	mainLabel = tk.Label(root, text='Infofönster')
	mainLabel.grid(row=0, column=0)

	mainButton = tk.Button(root, text='Click me', command=on_click)
	mainButton.grid()

	root.mainloop()
