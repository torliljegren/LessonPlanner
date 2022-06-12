# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk


class TimeStatWin(tk.Toplevel):

	def __init__(self, parent=None, lesson_entries: list=None):
		super().__init__(master=parent)
		self.lesson_entries = lesson_entries
		self.protocol("WM_DELETE_WINDOW", self.on_close)

		self.bg_frame = ttk.Frame(self)
		self.bg_frame.grid(row=0, column=0, sticky=tk.NSEW)

		# A frame that holds the heading
		self.top_frame = ttk.Frame(self.bg_frame)
		self.top_frame.grid(row=0, column=0, pady=(10,20), padx=20)
		ttk.Label(self.top_frame, text="Tidsstatistik", font=(None, 14, "bold")).grid(row=0, column=0)

		# A frame that holds the stat info
		self.stat_frame = ttk.Frame(self.bg_frame)
		self.stat_frame.grid(row=1, column=0, padx=10,pady=10)

		# A frame that holds the buttons
		self.btn_frame = ttk.Frame(self.bg_frame)
		self.btn_frame.grid(row=2, column=0, pady=10)
		ttk.Button(self.btn_frame, text="Stäng", command=self.on_close).grid(row=0, column=1, padx=(20,0))
		ttk.Button(self.btn_frame, text="Uppdatera", command=self.fill_time_stats).grid(row=0, column=0, padx=(0,20))

		# Fill the stat info frame
		ttk.Label(self.stat_frame, text="Total utlagd tid:").grid(row=0, column=0, pady=15, padx=(10,5),
																		  sticky="E")
		ttk.Label(self.stat_frame, text="Utlagd lektionstid:").grid(row=1, column=0, pady=15, padx=(10,5),
																		  sticky="E")
		ttk.Label(self.stat_frame, text="Utlagd tid innan NP:").grid(row=2, column=0, pady=15, padx=(10,5),
																				  sticky="E")
		ttk.Label(self.stat_frame, text="Utlagd lektionstid innan NP:").grid(row=3, column=0, pady=15, padx=(10,5),
																				  sticky="E")
		#ttk.Label(self.stat_frame, text="Antal planerade lektioner").grid(row=4, column=0, pady=15, padx=(10,5),
		#																  sticky="E")

		self.var_incl = tk.StringVar(self.stat_frame)
		self.entry_incl = ttk.Entry(self.stat_frame, textvariable=self.var_incl, state="readonly")
		self.entry_incl.grid(row=0, column=1, padx=(5,10))

		self.var_excl = tk.StringVar(self.stat_frame)
		self.entry_excl = ttk.Entry(self.stat_frame, textvariable=self.var_excl, state="readonly")
		self.entry_excl.grid(row=1, column=1, padx=(5,10))

		self.var_incl_bfinal = tk.StringVar(self.stat_frame)
		self.entry_incl_bfinal = ttk.Entry(self.stat_frame, textvariable=self.var_incl_bfinal, state="readonly")
		self.entry_incl_bfinal.grid(row=2, column=1, padx=(5,10))

		self.var_excl_bfinal = tk.StringVar(self.stat_frame)
		self.entry_excl_bfinal = ttk.Entry(self.stat_frame, textvariable=self.var_excl_bfinal, state="readonly")
		self.entry_excl_bfinal.grid(row=3, column=1, padx=(5,10))

		sep = ttk.Separator(master=self.stat_frame, orient=tk.HORIZONTAL)
		sep.grid(row=4, column=0, columnspan=2, sticky=tk.EW)

		#ttk.Label(self.stat_frame, text="Antal lektioner").grid(row=5, column=0)

		self.fill_time_stats()

		# self.update()
		# self.update_idletasks()

	def fill_time_stats(self):
		excl = self.calc_tot_notests()
		incl = self.calc_tot()
		excl_bfinal = self.calc_prefinal_notests()
		incl_bfinal = self.calc_prefinal()

		str_excl = self.mins_to_str(excl)
		str_incl = self.mins_to_str(incl)
		str_excl_bfinal = self.mins_to_str(excl_bfinal)
		str_incl_bfinal = self.mins_to_str(incl_bfinal)

		self.var_incl.set(str_incl)
		self.var_excl.set(str_excl)
		self.var_excl_bfinal.set(str_excl_bfinal)
		self.var_incl_bfinal.set(str_incl_bfinal)

	def find_final(self) -> int:
		keyws = ("np", "n.p", "n.p." "nationella", "nationella provet", "nationellt prov", "kursprov", "slutprov")
		for entry in reversed(self.lesson_entries):
			for kw in keyws:
				if kw in entry.var_topic.get().lower() and entry.var_test.get():
					# print("NP #:",entry.var_id.get())
					return int(entry.var_id.get())
		return 0

	def calc_tot_notests(self) -> int:
		tdur = 0

		# calculate hours and minutes of lesson time
		for entry in self.lesson_entries:
			if (not entry.var_cancelled.get()) and (not entry.var_test.get()):
				tdur += int(entry.var_duration.get())
			elif entry.var_cancelled.get() and entry.var_test.get():
				tdur += int(entry.var_duration.get())

		return tdur

	def calc_tot(self) -> int:
		tdur = 0

		# calculate minutes of lesson time
		for entry in self.lesson_entries:
			# skip cancelled lessons
			if not entry.var_test.get() and entry.var_cancelled.get():
				continue
			# include everything else
			else:
				tdur += int(entry.var_duration.get())

		return tdur

	def calc_prefinal_notests(self) -> int:
		tdur = 0
		lid = 1
		stop = self.find_final()

		for entry in self.lesson_entries:
			# return before including final
			if lid == stop:
				return tdur
			# include locked lessons
			elif entry.var_cancelled.get() and entry.var_test.get():
				tdur += int(entry.var_duration.get())
			# include ordinary lessons
			elif not entry.var_cancelled.get() and not entry.var_test.get():
				tdur += int(entry.var_duration.get())

			lid += 1

		return tdur

	def calc_prefinal(self) -> int:
		tdur = 0
		lid = 1
		stop = self.find_final()

		for entry in self.lesson_entries:
			# return before including final
			if lid == stop:
				return tdur
			# include tests
			elif not entry.var_cancelled.get() and entry.var_test.get():
				tdur += int(entry.var_duration.get())
			# include ordinary lessons
			elif not entry.var_cancelled.get() and not entry.var_test.get():
				tdur += int(entry.var_duration.get())
			# include locked lessons
			elif entry.var_cancelled.get() and entry.var_test.get():
				tdur += int(entry.var_duration.get())

			lid += 1

		return tdur

	def number_of_lessons(self) -> int:
		num = 0
		for lesson in self.lesson_entries:
			if lesson.var_cancelled.get() and not lesson.var_test.get():
				continue
			elif not lesson.var_cancelled.get() and lesson.var_test.get():
				continue
			else:
				num += 1
		return num

	def number_of_tests(self) -> int:
		num = 0
		for lesson in self.lesson_entries:
			if not lesson.var_cancelled.get() and lesson.var_test.get():
				num += 1
		return num

	def number_of_cancelled(self) -> int:
		num = 0
		if lesson.var_cancelled.get() and not lesson.var_test.get():
			num += 1
		return num


	def mins_to_str(self, mins: int) -> str:
		th = int(mins/60)
		tm = mins - th * 60
		return str(th) + " h " + str(tm) + " min"


	def on_close(self):
		self.destroy()
