# encoding: utf-8

from tkinter import *

import Constants


class LessonEntry(object):
    def __init__(self, lesson, target, upd_time_func, _relief=None, move_all=False, _font=None, _bg=None,
                 _weekfont=None, _idfont=None, _dayfont=None):

        self.target = target

        # the model object "lesson" is only updated when update_model() is called
        self.lesson = lesson

        self.update_time_count = upd_time_func

        self.odd = lesson.is_odd

        self.ab_week = self.lesson.week_ab

        # so that the original day can be restored
        self.original_day = lesson.day

        # so that the original duration can be restored
        self.original_duration = lesson.duration_min

        # if True MainWin.move_up() and move_down() will also move week and day
        # (to enable insertion of new lessons in arbitrary weeks
        self.move_all = move_all

        self.var_week = StringVar(target, value=str(lesson.week)+self.ab_week)
        self.label_week = Label(target, textvariable=self.var_week, font=_weekfont, bg=_bg)

        self.var_day = StringVar(target, value=lesson.day)
        self.label_day = Label(target, textvariable=self.var_day, font=_dayfont, bg=_bg)

        self.var_id = StringVar(target, value=str(lesson.id))
        self.label_id = Label(target, textvariable=self.var_id, font=_idfont, bg=_bg)

        self.var_topic = StringVar(target)
        self.entry_topic = Entry(target, textvariable=self.var_topic, width=30, relief=_relief, font=_font, bg=_bg,
                                 highlightcolor=Constants.ENTRY_COLOR, highlightbackground=Constants.ENTRY_COLOR,
                                 highlightthickness=1)

        self.var_pages = StringVar(target)
        self.entry_pages = Entry(target, textvariable=self.var_pages, relief=_relief, font=_font, bg=_bg, width=14,
                                 highlightcolor=Constants.ENTRY_COLOR, highlightbackground=Constants.ENTRY_COLOR,
                                 highlightthickness=1)

        self.var_assignment = StringVar(target)
        self.entry_assignment = Entry(target, textvariable=self.var_assignment, relief=_relief, font=_font, bg=_bg,
                                      width=14, highlightcolor=Constants.ENTRY_COLOR,
                                      highlightbackground=Constants.ENTRY_COLOR, highlightthickness=1)

        self.var_link = StringVar(target)
        self.entry_link = Entry(target, textvariable=self.var_link, relief=_relief, font=_font, bg=_bg, width=14,
                                 highlightcolor=Constants.ENTRY_COLOR, highlightbackground=Constants.ENTRY_COLOR,
                                 highlightthickness=1)

        self.var_test = BooleanVar(target)
        self.checkbox_test = Checkbutton(target, variable=self.var_test, command=self.test_pressed,
                                         font=_font, bg=Constants.TEST_COLOR)

        self.var_cancelled = BooleanVar(target)
        self.checkbox_cancelled = Checkbutton(target, variable=self.var_cancelled, bg=Constants.CANCELLED_COLOR,
                                              command=self.cancelled_pressed, font=_font)

        self.var_selected = BooleanVar(target)
        self.checkbox_selected = Checkbutton(target, variable=self.var_selected, command=self.selected_pressed,
                                             font=_font, bg=_bg)

        self.var_duration = StringVar(target, value=self.lesson.duration_min)
        self.label_duration = Label(target, textvariable=self.var_duration, font=_idfont, bg=_bg)

    # returns True if this entry is empty, false otherwise
    def empty(self) -> bool:
        if self.var_topic.get():
            return False
        elif self.var_pages.get():
            return False
        elif self.var_assignment.get():
            return False
        elif self.var_test.get():
            return False
        elif self.var_cancelled.get():
            return False
        else:
            return True

    def week(self) -> int:
        week = self.var_week.get()
        week = week.strip("A")
        week = week.strip("B")
        return int(week)

    def week_set(self, wknr):
        self.var_week.set(wknr + self.ab_week)

    def aorb(self) -> str:
        if list(self.var_week.get())[-1] == "A":
            return "A"
        elif list(self.var_week.get())[-1] == "B":
            return "B"
        else:
            return ""

    # Updates the model object to reflect the values altered in the UI
    def update_model(self):
        self.lesson.week = self.week()
        self.lesson.week_ab = self.aorb()
        self.lesson.day = self.var_day.get()
        self.lesson.id = self.var_id.get()
        self.lesson.topic = self.var_topic.get()
        self.lesson.pages = self.var_pages.get()
        self.lesson.assignment = self.var_assignment.get()
        self.lesson.is_test = self.var_test.get()
        self.lesson.is_cancelled = self.var_cancelled.get()

        # check if unnoticed oddness is there
        if self.label_day.cget("fg") == Constants.ODD_COLOR:
            self.odd = True
        self.lesson.is_odd = self.odd
        self.lesson.duration_min = self.var_duration.get()
        self.lesson.link = self.var_link.get()
        # disregard "selected" checkbox - its only a GUI thing

    # updates the GUI to reflect the model object
    def update_GUI(self):
        self.var_week.set(str(self.lesson.week) + self.lesson.week_ab)
        self.var_day.set(self.lesson.day)
        self.var_topic.set(self.lesson.topic)
        self.var_pages.set(self.lesson.pages)
        self.var_assignment.set(self.lesson.assignment)
        self.var_duration.set(self.lesson.duration_min)
        self.var_link.set(self.lesson.link)

        if self.lesson.is_test:
            self.color_row(Constants.TEST_COLOR)
        self.var_test.set(self.lesson.is_test)

        if self.lesson.is_cancelled:
            self.color_row(Constants.CANCELLED_COLOR)
        self.var_cancelled.set(self.lesson.is_cancelled)

        if self.lesson.is_test and self.lesson.is_cancelled:
            self.color_row(Constants.POSLOCK_COLOR)

        if self.lesson.is_odd:
            self.label_day.config(fg=Constants.ODD_COLOR)


    def clear_entries(self):
        self.var_topic.set("")
        self.var_pages.set("")
        self.var_assignment.set("")
        self.var_link.set("")

        # restore to original time if cancelled or test
        if self.var_cancelled.get() or self.var_test.get():
            self.var_duration.set(self.original_duration)
            # print("Original time", self.original_duration, "set on nr", self.var_id.get())

        # restore checkboxes
        self.var_test.set(False)
        self.var_cancelled.set(False)
        self.color_row(Constants.SEL_COLOR if self.var_selected.get() else Constants.BG_COLOR)

        # restore original day if changed
        if self.var_day.get() != self.original_day and not self.odd:
            self.var_day.set(self.original_day)
            self.label_day.configure(fg="black")

    def cancelled_pressed(self):
        color = "white"
        c_state = self.var_cancelled.get()
        t_state = self.var_test.get()

        # if test was already active and cancelled turned on
        if c_state and t_state:
            # deactivate test then change color
            # self.var_test.set(False)
            color = Constants.POSLOCK_COLOR
            self.var_duration.set(self.original_duration)
        # if test was off and cancelled turned on
        elif c_state:
            # change the color
            color = Constants.CANCELLED_COLOR
            self.var_duration.set("0")
        else:
            self.checkbox_test.deselect()
            self.var_duration.set(self.original_duration)
            color = Constants.BG_COLOR

        self.update_time_count()
        self.color_row(color)

    def test_pressed(self):
        color = "white"
        c_state = self.var_cancelled.get()
        t_state = self.var_test.get()

        # if cancelled was already active and test turned on
        if c_state and t_state:
            # deactivate cancelled then change color
            # self.var_cancelled.set(False)
            color = Constants.POSLOCK_COLOR
            self.var_duration.set(self.original_duration)

        # if cancelled was off and test turned on
        elif t_state:
            # change the color
            color = Constants.TEST_COLOR
            self.var_duration.set("180")

        # when both are switched off, restore original length and color
        else:
            self.checkbox_cancelled.deselect()
            self.var_duration.set(self.original_duration)
            color = Constants.BG_COLOR

        # self.main_timevar.set(int(self.main_timevar.get()) + int(self.var_duration.get()) - o_time)
        # print("cancelled_pressed: time diff is", int(self.var_duration.get()) - o_time)
        self.update_time_count()
        self.color_row(color)

    def selected_pressed(self):
        s_state = self.var_selected.get()
        c_state = self.var_cancelled.get()
        t_state = self.var_test.get()

        if s_state:
            self.color_row(Constants.SEL_COLOR)
        elif c_state:
            self.cancelled_pressed()
        elif t_state:
            self.test_pressed()
        else:
            self.color_row(Constants.BG_COLOR)
        self.entry_topic.focus_set()

    def color_row(self, color):
        e1, e2, e3, e4 = self.get_entry_widgets()
        e1.config(bg=color)
        e2.config(bg=color)
        e3.config(bg=color)
        e4.config(bg=color)
        # print("color_row(): coloring row",self.lesson.id, color)

    def refresh_color(self):
        if self.var_cancelled.get() and self.var_test.get():
            self.color_row(Constants.POSLOCK_COLOR)
        elif self.var_cancelled.get():
            self.color_row(Constants.CANCELLED_COLOR)
        elif self.var_test.get():
            self.color_row(Constants.TEST_COLOR)
        else:
            self.color_row(Constants.BG_COLOR)

        if self.odd:
            self.label_day.config(fg=Constants.ODD_COLOR)
        else:
            self.label_day.config(fg="#000000")


    def grid(self, lesson_row, first_col, _padx=0, _pady=0):
        self.label_week.grid(row=lesson_row, column=first_col, padx=_padx, pady=_pady)
        self.label_day.grid(row=lesson_row, column=first_col + 1, padx=_padx, pady=_pady)
        self.label_id.grid(row=lesson_row, column=first_col + 2, padx=_padx, pady=_pady)
        self.checkbox_selected.grid(row=lesson_row, column=first_col + 3, padx=_padx, pady=_pady)
        self.entry_topic.grid(row=lesson_row, column=first_col + 4, padx=_padx, pady=_pady)
        self.entry_pages.grid(row=lesson_row, column=first_col + 5, padx=_padx, pady=_pady)
        self.entry_assignment.grid(row=lesson_row, column=first_col + 6, padx=_padx, pady=_pady)
        self.entry_link.grid(row=lesson_row, column=first_col + 7, padx=_padx, pady=_pady)
        self.checkbox_test.grid(row=lesson_row, column=first_col + 8, padx=_padx, pady=_pady)
        self.checkbox_cancelled.grid(row=lesson_row, column=first_col + 9, padx=_padx, pady=_pady)
        self.label_duration.grid(row=lesson_row, column=first_col + 10, padx=_padx, pady=_pady)

        # color the entries white to match the other color setting methods
        self.entry_topic.configure(bg=Constants.BG_COLOR)
        self.entry_pages.configure(bg=Constants.BG_COLOR)
        self.entry_assignment.configure(bg=Constants.BG_COLOR)
        self.entry_link.configure(bg=Constants.BG_COLOR)

    # Returns the four entry widgets
    def get_entry_widgets(self):
        return self.entry_topic, self.entry_pages, self.entry_assignment, self.entry_link

    # Destroys this entrys widgets
    def destroy(self):
        self.label_week.grid_forget()
        self.label_week.destroy()

        self.label_day.grid_forget()
        self.label_day.destroy()

        self.label_id.grid_forget()
        self.label_id.destroy()

        self.entry_topic.grid_forget()
        self.entry_topic.destroy()

        self.entry_pages.grid_forget()
        self.entry_pages.destroy()

        self.entry_assignment.grid_forget()
        self.entry_assignment.destroy()

        self.checkbox_test.grid_forget()
        self.checkbox_test.destroy()

        self.checkbox_cancelled.grid_forget()
        self.checkbox_cancelled.destroy()

        self.checkbox_selected.grid_forget()
        self.checkbox_selected.destroy()

        self.label_duration.grid_forget()
        self.label_duration.destroy()

        self.entry_link.grid_forget()
        self.entry_link.destroy()

    def __str__(self) -> str:
        return self.lesson.__str__()
