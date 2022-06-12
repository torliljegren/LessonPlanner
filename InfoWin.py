# encoding: utf-8

import tkinter.messagebox
import tkinter.ttk as ttk
from Constants import *
from MainWin import *
from Subject import *


class InfoWin(Tk):
    def __init__(self):

        super().__init__()
        # self.opened_mainwins = []
        self.destroyed = False
        self.withdraw()
        self.attributes('-alpha', 0)
        self.title("Ny planering")
        self.resizable(False, False)

        if platform.system() == "Linux":
            self.style = tkinter.ttk.Style()
            self.style.theme_use("clam")

        # Create GUI elements

        self.mainframe = ttk.Frame(self)
        self.entry_strip = ttk.Frame(self.mainframe)
        self.button_strip = ttk.Frame(self.mainframe)

        self.label_heading = ttk.Label(self.mainframe, text="Fyll i kursinformation", font=TITLE_FONT)

        self.label_subject = ttk.Label(self.entry_strip, text="Kursnamn: ", font=HEADING_FONT)
        self.var_subject = StringVar(self.entry_strip)
        self.entry_subject = ttk.Entry(self.entry_strip, textvariable=self.var_subject)

        self.label_class = ttk.Label(self.entry_strip, text="Klass: ", font=HEADING_FONT)
        self.var_class = StringVar(self.entry_strip)
        self.entry_class = ttk.Entry(self.entry_strip, textvariable=self.var_class)

        self.label_start = ttk.Label(self.entry_strip, text="Startvecka: ", font=HEADING_FONT)
        self.var_start = StringVar(self.entry_strip)
        self.entry_start = ttk.Entry(self.entry_strip, textvariable=self.var_start)

        self.label_end = ttk.Label(self.entry_strip, text="Slutvecka: ", font=HEADING_FONT)
        self.var_end = StringVar(self.entry_strip)
        self.entry_end = ttk.Entry(self.entry_strip, textvariable=self.var_end)

        self.label_days = ttk.Label(self.entry_strip, text="Lektionsdag(ar): ", font=HEADING_FONT)
        self.var_days = StringVar(self.entry_strip)
        self.entry_days = ttk.Entry(self.entry_strip, textvariable=self.var_days)

        self.button_ok = ttk.Button(self.button_strip, text="Klar", width=10, command=self.ok_press)
        self.button_load = ttk.Button(self.button_strip, text="Öppna", width=10, command=self.load_press)

        # prepare the advanced GUI
        self.advanced_frame = ttk.Frame(self.mainframe)
        self.var_advanced = BooleanVar(self)
        self.button_advanced = ttk.Checkbutton(self.button_strip, text="A/B-veckor", command=self.show_advanced,
                                               variable=self.var_advanced)

        self.label_a_days = ttk.Label(self.advanced_frame, text="Dag(ar) A-vecka: ", font=HEADING_FONT)
        self.var_a_days = StringVar(self.advanced_frame)
        self.entry_days_a = ttk.Entry(self.advanced_frame, textvariable=self.var_a_days)

        self.label_b_days = ttk.Label(self.advanced_frame, text="Dag(ar) B-vecka: ", font=HEADING_FONT)
        self.var_b_days = StringVar(self.advanced_frame)
        self.entry_days_b = ttk.Entry(self.advanced_frame, textvariable=self.var_b_days)

        self.label_breaks = ttk.Label(self.advanced_frame, text="Lovveckor: ", font=HEADING_FONT)
        self.var_breaks = StringVar(self.advanced_frame)
        self.entry_breaks = ttk.Entry(self.advanced_frame, textvariable=self.var_breaks)


        self.setup_info_gui()

        self.bind("<Return>", lambda u: self.ok_press())
        self.protocol("WM_DELETE_WINDOW", self.on_quit)

        # center the window
        # avoid unwanted "flashing" by making window transparent until fully ready
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 6) #- (h / 2)
        self.geometry('+%d+%d' % (x, y))
        self.attributes('-alpha', 1)
        self.deiconify()

    def setup_info_gui(self):
        # Layout GUI elements
        paddy=4
        self.mainframe.grid(row=0, column=0, sticky="nsew")
        self.entry_strip.grid(row=1, column=1, padx=60)
        self.button_strip.grid(row=2,column=1, columnspan=2, pady=20)

        self.label_heading.grid(row=0, column=1, pady=20, padx=10, columnspan=2)

        self.label_subject.grid(row=2, column=1, sticky="E")
        self.entry_subject.grid(row=2, column=2, pady=paddy)

        self.label_class.grid(row=3, column=1, sticky="E")
        self.entry_class.grid(row=3, column=2, pady=paddy)

        self.label_start.grid(row=4, column=1, sticky="E")
        self.entry_start.grid(row=4, column=2, pady=paddy)

        self.label_end.grid(row=5, column=1, sticky="E")
        self.entry_end.grid(row=5, column=2, pady=paddy)

        self.label_days.grid(row=6, column=1, sticky="E")
        self.entry_days.grid(row=6, column=2, pady=paddy)

        self.button_ok.grid(row=1, column=1, padx=10, pady=10)
        self.button_load.grid(row=1, column=2,padx=10,pady=10)
        self.button_advanced.grid(row=1, column=3, padx=10, pady=10)

        self.label_a_days.grid(row=2, column=1, sticky="E")
        self.entry_days_a.grid(row=2, column=2, pady=paddy)

        self.label_b_days.grid(row=3, column=1, sticky="E")
        self.entry_days_b.grid(row=3, column=2, pady=paddy)

        self.label_breaks.grid(row=4, column=1, sticky="E")
        self.entry_breaks.grid(row=4, column=2, pady=paddy)
        self.var_breaks.set("44, 52, 1, 9, 14")

        ttk.Label(master=self.advanced_frame,
                  text="(Startveckan blir en A-vecka och A/B-veckor\nkommer att skippa lovveckorna.)",
                  font=INFO_FONT).grid(row=1, column=1, pady=10, columnspan=2)

        ttk.Label(master=self.advanced_frame, text=" ").grid(row=5, column=1, pady=10)

    def show_advanced(self):
        if self.var_advanced.get():
            self.entry_days.config(state="disabled")
            self.advanced_frame.grid(row=3, column=1, pady=0, padx=30)
            self.var_breaks.set("44, 52, 1, 9, 14")
        else:
            self.entry_days.config(state="enabled")
            self.advanced_frame.grid_forget()

    def on_quit(self):
        if self.destroyed:
            pass
        else:
            self.destroyed = True
            self.destroy()

    def ok_press(self):
        # Create the subject from info from entries
        s_name = self.entry_subject.get()
        group = self.entry_class.get()
        start = 0
        end = 0
        try:
            start = int(self.entry_start.get())
        except ValueError:
            tkinter.messagebox.showerror(title="Fel startvecka", message="Startveckan "+self.entry_start.get()+
                                                                         " är inte en giltig vecka")
            return

        try:
            end = int(self.entry_end.get())
        except ValueError:
            tkinter.messagebox.showerror(title="Fel slutvecka", message="Slutveckan "+self.entry_end.get()+
                                                                        " är inte en giltig vecka")
            return

        if end<1:
            tkinter.messagebox.showerror(title="Fel slutvecka", message="Slutveckan " + self.entry_end.get() +
                                                                        " är inte en giltig vecka")
            return
        elif start<1:
            tkinter.messagebox.showerror(title="Fel startvecka", message="Startveckan " + self.entry_start.get() +
                                                                         " är inte en giltig vecka")
            return
        elif start>52:
            tkinter.messagebox.showerror(title="Fel startvecka", message="Startveckan " + self.entry_start.get() +
                                                                         " är inte en giltig vecka")
            return
        elif end>52:
            tkinter.messagebox.showerror(title="Fel slutvecka", message="Slutveckan " + self.entry_end.get() +
                                                                        " är inte en giltig vecka")
            return

        # handle when the user has selected a/b-weeks
        if self.var_advanced.get():
            self.handle_advanced_ok()
            return
        days = ()
        days_str = self.entry_days.get()
        if days_str:
            if "," in days_str:
                days = tuple(days_str.lower().replace(" ", "").split(","))  # remove spaces and convert to array
            elif ";" in days_str:
                days = tuple(days_str.lower().replace(" ", "").split(";"))
            else:
                days = tuple(days_str.lower().split(" "))
        else:
            days = tuple("Tom")

        # check if days are ok, warn if not
        inv_days = Lesson.get_invalid_days(days)
        if inv_days:
            tkinter.messagebox.showwarning(master=self, title="Fel",
                                           message="Följande dag(ar) är inte gilitga:\n" + " ".join(inv_days))
            return

        # create a subject from the info in the GUI
        filled_subject = Subject(name=s_name, group=group, start_week=start, end_week=end, lesson_days=days)
        # print("InfoWin: start =", start, "end =", end)
        filled_subject.create_lessons()
        # Open the main window and hide the first info window
        self.clear_entries()
        self.withdraw()
        main_win = MainWin(filled_subject, parent=self)
        main_win.mainloop()

    def handle_advanced_ok(self):
        days_a_str = self.var_a_days.get()
        days_b_str = self.var_b_days.get()
        break_weeks_str = self.var_breaks.get()

        days_a = ()
        days_b = ()
        break_weeks = ()

        # remove spaces and convert to array, using ';' and ',' as delimiters if present
        if "," in days_a_str:
            days_a = tuple(days_a_str.lower().replace(" ", "").split(","))
        elif ";" in days_a_str:
            days_a = tuple(days_a_str.lower().replace(" ", "").split(";"))
        else:
            days_a = tuple(days_a_str.lower().split(" "))

        if "," in days_b_str:
            days_b = tuple(days_b_str.lower().replace(" ", "").split(","))
        elif ";" in days_b:
            days_b = tuple(days_b_str.lower().replace(" ", "").split(";"))
        else:
            days_b = tuple(days_b_str.lower().split(" "))

        if "," in break_weeks_str:
            break_weeks = tuple(break_weeks_str.lower().replace(" ", "").split(","))
        elif ";" in break_weeks_str:
            break_weeks = tuple(break_weeks_str.lower().replace(" ", "").split(";"))
        else:
            break_weeks = tuple(break_weeks_str.lower().split(" "))

        if len(break_weeks) > 0:
            break_weeks = map(int, break_weeks)

        # check if days are ok, warn if not
        inv_days_a = Lesson.get_invalid_days(days_a)
        if inv_days_a:
            tkinter.messagebox.showwarning(master=self, title="Fel",
                                           message="Följande A-dag(ar) är inte gilitga:\n" + " ".join(inv_days_a))
            return

        inv_days_b = Lesson.get_invalid_days(days_b)
        if inv_days_b:
            tkinter.messagebox.showwarning(master=self, title="Fel",
                                           message="Följande B-dag(ar) är inte gilitga:\n" + " ".join(inv_days_b))
            return

        # create a subject from the info in the GUI
        filled_subject = Subject(name=self.entry_subject.get(), group=self.entry_class.get(),
                                 start_week=int(self.entry_start.get()), end_week=int(self.entry_end.get()),
                                 lesson_days_a=days_a, lesson_days_b=days_b, week_breaks=break_weeks)

        filled_subject.create_lessons_ab()
        # for lesson in filled_subject.all_lessons:
        #    print(lesson)

        self.clear_entries()
        self.withdraw()

        # Create and open the main window and close the first info window
        main_win = MainWin(filled_subject, parent=self)
        main_win.mainloop()

    def load_press(self):
        self.withdraw()
        self.clear_entries()
        MainWin.open_csv(self)

    def clear_entries(self):
        self.var_subject.set("")
        self.var_class.set("")
        self.var_start.set("")
        self.var_end.set("")
        self.var_days.set("")
        self.var_a_days.set("")
        self.var_b_days.set("")
        self.var_breaks.set("")
        if self.var_advanced.get():
            self.button_advanced.invoke()

# ENTRY POINT
if __name__ == "__main__":
    # open the info window
    app_start = InfoWin()
    #MainWin.center_window(app_start)
    app_start.mainloop()
