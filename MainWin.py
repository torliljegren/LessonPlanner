# encoding: utf-8

from tkinter import *
from tkinter import ttk
import tkinter.simpledialog
import tkinter.filedialog
import tkinter.messagebox
import tkinter.dialog

from tktooltip import ToolTip

import time
import threading

import Constants
from Constants import *
from ScrollbarFrame import ScrollbarFrame
from Subject import Subject
from Lesson import Lesson
from LessonEntry import LessonEntry
from ChangeDayDialog import ChangeDayDialog
from NewLessonDialog import NewLessonDialog
from ChangeTitleDialog import ChangeTitleDialog
from ChangeInfoDialog import ChangeInfoDialog
from ChangeDurationDialog import ChangeDurationDialog
from AboutWin import AboutWin
from TimeStatWin import TimeStatWin
import SubjectToExcel as sx
import SubjectToExcelM as sxm

import csv
import platform
import sys


class MainWin(Toplevel):
    def __init__(self, subject, parent=None, fpath=None):
        super().__init__(master=parent, takefocus=False)

        # keep track of status of self
        self.destroyed = False

        # keep track of time since last save (stops at 10 s which is max before asktosave box triggers at exit)
        self.seconds_since_save = Constants.DONOTASK_SAVE_TIME
        self.sec_thread = threading.Thread(target=self.count_since_save)

        # hide the window until it's ready
        self.withdraw()
        self.attributes('-alpha', 0)

        # a reference to the parent (InfoWin)
        self.parent = parent

        # a reference to the path of the opened csv
        self.fpath = fpath

        # a reference to the window that opened this
        self.parent = parent


        # The model object of a subject, which contains all lessons and some info
        self.subject = subject

        # A list of LessonEntries to be drawn
        self.lesson_entries = []

        # Saves the
        self.undo_buffer = []

        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)

        # Create a frame for the canvas and scrollbar(s).
        self.frame = ScrollbarFrame(self)
        self.frame.grid(row=1, column=0, sticky="ew")

        # bind the mouse wheel to the scrollbar
        if platform.system() == "Linux":
            self.frame.canvas.bind_all("<4>", self.scrolling_linux)
            self.frame.canvas.bind_all("<5>", self.scrolling_linux)
        else:
            self.frame.canvas.bind_all("<MouseWheel>", self.scrolling)

        # Create a frame on to contain the buttons.
        self.lessons_frame = self.frame.scrolled_frame
        self.lessons_frame.config(bg=BG_COLOR)

        # stores lesson duration total for LessonEntry to work with to update the time when cancelled or test i pressed
        self.total_minutes = 0

        ################################
        #           HEADINGS           #
        ################################

        info_str = subject.teacher + ", " + subject.school if subject else "Lärare, Skola"
        self.var_info = StringVar(self.lessons_frame, value=info_str)
        self.info_label = Label(self.lessons_frame, textvariable=self.var_info, font=INFO_FONT, bg=BG_COLOR)
        self.info_label.grid(row=0, column=1, pady=(1, 0), padx=(1, 0), sticky="W", columnspan=10)

        heading = (subject.name + " med " + subject.group) if (subject.name and subject.group) else "Kurs med klass"
        self.var_heading = StringVar(self.lessons_frame, value=heading)
        self.heading_label = Label(self.lessons_frame, textvariable=self.var_heading, font=TITLE_FONT, bg=BG_COLOR)
        self.heading_label.grid(row=1, column=1, pady=20, columnspan=11)

        self.week_label = Label(self.lessons_frame, text="Vecka", font=HEADING_FONT, bg=BG_COLOR)
        self.week_label.grid(row=2, column=1)

        self.day_label = Label(self.lessons_frame, text="Dag", font=HEADING_FONT, bg=BG_COLOR)
        self.day_label.grid(row=2, column=2)

        self.id_label = Label(self.lessons_frame, text="#", font=HEADING_FONT, bg=BG_COLOR)
        self.id_label.grid(row=2, column=3)

        # self.selected_label = Label(self.lessons_frame, text="✓", font=(None, 14, "normal"), bg=BG_COLOR)
        # self.selected_label.grid(row=2, column=4)

        self.topic_label = Label(self.lessons_frame, text="Innehåll", font=HEADING_FONT, bg=BG_COLOR)
        self.topic_label.grid(row=2, column=5)

        self.pages_label = Label(self.lessons_frame, text="Sidor", font=HEADING_FONT, bg=BG_COLOR)
        self.pages_label.grid(row=2, column=6)

        self.assignment_label = Label(self.lessons_frame, text="Övrigt", font=HEADING_FONT, bg=BG_COLOR)
        self.assignment_label.grid(row=2, column=7)

        self.link_label = Label(self.lessons_frame, text="Videoklipp", font=HEADING_FONT, bg=BG_COLOR)
        self.link_label.grid(row=2, column=8)

        self.test_label = Label(self.lessons_frame, text="Prov", font=HEADING_FONT, bg=BG_COLOR)
        self.test_label.grid(row=2, column=9)

        self.cancelled_label = Label(self.lessons_frame, text="Inställd", font=HEADING_FONT, bg=BG_COLOR)
        self.cancelled_label.grid(row=2, column=10)

        self.duration_label = Label(self.lessons_frame, text="Tid (min)", font=HEADING_FONT, bg=BG_COLOR)
        self.duration_label.grid(row=2, column=11)

        ################################
        #            TOOLBAR           #
        ################################
        ttpdelay = 0.5 # tooltip delay

        self.button_strip = Frame(master=self, borderwidth=1, highlightbackground="#D7D7D7", highlightthickness=3,
                             bg="#F6F6F6")
        self.button_strip.grid(row=0, column=0, sticky="ew")

        self.load_image = PhotoImage(file="open.png")
        load_button = Button(master=self.button_strip, image=self.load_image, command=lambda: self.open_csv(infowin=self.parent),
                             background=BUTTON_COLOR, relief=BUTTON_RELIEF,
                             highlightbackground=BUTTON_HLCOLOR)
        load_button.grid(row=0, column=0, padx=(10, 2))
        ToolTip(load_button, "Öppna", delay=ttpdelay, follow=False)

        self.save_image = PhotoImage(file="save.png")
        self.check_image = PhotoImage(file="check.png")
        self.save_button = Button(master=self.button_strip, image=self.save_image, command=self.save_csv, background=BUTTON_COLOR,
                             relief=BUTTON_RELIEF, highlightbackground=BUTTON_HLCOLOR)
        self.save_button.grid(row=0, column=1, padx=(2, 10))
        ToolTip(self.save_button, "Spara", delay=ttpdelay, follow=False)

        self.up_image = PhotoImage(file="up.png")
        up_button = Button(master=self.button_strip, image=self.up_image, command=self.up_pressed, background=BUTTON_COLOR,
                           relief=BUTTON_RELIEF, highlightbackground=BUTTON_HLCOLOR)
        up_button.grid(row=0, column=2, padx=(10, 2), pady=10)
        ToolTip(up_button, "Flytta upp lektion", delay=ttpdelay, follow=False)

        self.down_image = PhotoImage(file="down.png")
        down_button = Button(master=self.button_strip, image=self.down_image, command=self.down_pressed,
                             background=BUTTON_COLOR, relief=BUTTON_RELIEF, highlightbackground=BUTTON_HLCOLOR)
        down_button.grid(row=0, column=3, padx=(2, 10), pady=10)
        ToolTip(down_button, "Flytta ned lektion", delay=ttpdelay, follow=False)

        self.move_image = PhotoImage(file="move.png")
        move_button = Button(master=self.button_strip, image=self.move_image, command=self.move_pressed,
                             background=BUTTON_COLOR, relief=BUTTON_RELIEF, highlightbackground=BUTTON_HLCOLOR)
        move_button.grid(row=0, column=4, padx=(10, 10), pady=10)
        ToolTip(move_button, "Flytta lektion till", delay=ttpdelay, follow=False)

        self.new_image = PhotoImage(file="new2.png")
        new_button = Button(master=self.button_strip, image=self.new_image, command=self.new_empty_pressed,
                            background=BUTTON_COLOR, relief=BUTTON_RELIEF, highlightbackground=BUTTON_HLCOLOR)
        new_button.grid(row=0, column=5, padx=(10, 2), pady=10)
        ToolTip(new_button, "Infoga tom rad", delay=ttpdelay, follow=False)

        self.remove_image = PhotoImage(file="delete.png")
        remove_button = Button(master=self.button_strip, image=self.remove_image,
                               command=lambda:self.remove_row(undo=True), background=BUTTON_COLOR,
                               relief=BUTTON_RELIEF, highlightbackground=BUTTON_HLCOLOR)
        remove_button.grid(row=0, column=6, padx=(2, 10), pady=10)
        ToolTip(remove_button, "Ta bort rad", delay=ttpdelay, follow=False)

        self.clear_image = PhotoImage(file="clear.png")
        clear_button = Button(master=self.button_strip, image=self.clear_image, command=lambda:self.clear_row(undo=True),
                              background=BUTTON_COLOR, relief=BUTTON_RELIEF, highlightbackground=BUTTON_HLCOLOR)
        clear_button.grid(row=0, column=8, padx=(10, 10), pady=10)
        ToolTip(clear_button, "Rensa lektionens innehåll", delay=ttpdelay, follow=False)

        self.odd_image = PhotoImage(file="new.png")
        insert_odd_button = Button(master=self.button_strip, image=self.odd_image, command=self.create_odd_lesson,
                                   background=BUTTON_COLOR, relief=BUTTON_RELIEF, highlightbackground=BUTTON_HLCOLOR)
        insert_odd_button.grid(row=0, column=7, padx=(10, 10), pady=10)
        ToolTip(insert_odd_button, "Skapa ny lektion", delay=ttpdelay, follow=False)

        self.bomb_image = PhotoImage(file="bomb.png")
        remove_all_button = Button(master=self.button_strip, image=self.bomb_image, command=self.bomb_pressed,
                                   background=BUTTON_COLOR, relief=BUTTON_RELIEF, highlightbackground=BUTTON_HLCOLOR)
        remove_all_button.grid(row=0, column=9, padx=(10, 10), pady=10)
        ToolTip(remove_all_button, "Ta bort lektion från planeringen", delay=ttpdelay, follow=False)

        all_var = BooleanVar(master=self.button_strip)
        self.all_checkbox = Checkbutton(master=self.button_strip, text="Alla", variable=all_var, command=self.all_select,
                                        bg="#F6F6F6")
        self.all_checkbox.grid(row=0, column=10, sticky="E", padx=30)
        ToolTip(self.all_checkbox, "Markera alla/avmarkera valda", delay=ttpdelay, follow=False)

        self.var_time = StringVar(self.button_strip, value="Lektionstid: 0 h, 0 min")
        self.label_time = ttk.Entry(master=self.button_strip, textvariable=self.var_time, state="readonly")
        self.label_time.grid(row=0, column=11)
        ToolTip(self.label_time, "Klicka för att visa statistik", delay=ttpdelay, follow=False)

        ################################
        #           MENUBAR            #
        ################################

        self.menubar = Menu(self)

        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Ny planering"+16*" ", command=self.new_doc_pressed)
        filemenu.add_command(label="Öppna", command=lambda:self.open_csv(infowin=self.parent))
        filemenu.add_command(label="Spara", command=self.save_csv)
        filemenu.add_command(label="Spara som", command=lambda:self.save_csv(saveas=True))

        filemenu.add_separator()

        filemenu.add_command(label="Avsluta", command=lambda: sys.exit(0))

        self.menubar.add_cascade(label="Arkiv", menu=filemenu)

        toolsmenu = Menu(self.menubar, tearoff=0)
        toolsmenu.add_command(label="Ångra", command=self.undo_restore)
        toolsmenu.add_command(label="Rensa", command=self.clear_row)
        toolsmenu.add_command(label="Välj alla", command=self.select_all)

        toolsmenu.add_separator()

        toolsmenu.add_command(label="Samla ihop valda", command=lambda: self.gather_sel(undo=True))
        toolsmenu.add_command(label="Lägg till vecka", command=lambda: self.create_new_week(scroll=True))
        toolsmenu.add_command(label="Dela lektion", command=self.split_row)
        toolsmenu.add_command(label="Slå ihop valda lektioner", command=self.merge_command)
        toolsmenu.add_command(label="Byt A/B-vecka", command=self.swap_ab_on_focused_week)

        toolsmenu.add_separator()

        toolsmenu.add_command(label="Importera lektioner", command=self.import_csv)
        toolsmenu.add_command(label="Exportera till Excel (lista)", command=self.export_excel)
        toolsmenu.add_command(label="Exportera till Excel (veckor)", command=lambda:self.export_excel(layout="mattias"))

        self.menubar.add_cascade(label="Verktyg", menu=toolsmenu)

        helpmenu = Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="Om...", command=lambda: AboutWin(self).mainloop())
        helpmenu.add_command(label="Manual", command=lambda: tk.messagebox.showinfo(title="Manual",
                                                                                    message=HELPMSG))
        self.menubar.add_cascade(label="Hjälp", menu=helpmenu)

        self.config(menu=self.menubar)

        ################################
        #  INIT LESSONS AND BINDINGS   #
        ################################

        if self.subject is not None:
            self.create_lesson_entries()
            self.update_time_count()

        if parent is not None:
            parent.withdraw()

        # bind enter key to move focus down one step
        self.bind("<Return>", self.focus_down)

        # bind ctrl+z to undo
        self.bind_all("<Control-z>", lambda e: self.undo_restore())

        # bind a mouse click on the heading to trigger ChangeTitleDialog
        self.heading_label.bind("<Button-1>", self.heading_clicked)

        # bind a mouse click on the teacher/school info to trigger ChangeInfoDialog
        self.info_label.bind("<Button-1>", self.info_clicked)

        # handle window closing by showing InfoWin again
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # bind duration counter to TimeStatWin
        self.label_time.bind("<Button-1>", lambda e: TimeStatWin(self, self.lesson_entries).mainloop())

        # center the window
        # Avoid unwanted "flashing" by making window transparent until fully ready
        # self.update()
        self.update_idletasks()
        w = self.winfo_reqwidth()
        # h = self.winfo_reqheight()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 8) if platform.system() == "Darwin" else 0
        self.update_wintitle()

        if platform.system() == "Linux":
            self.style = tkinter.ttk.Style()
            self.style.theme_use("clam")

        self.geometry('+%d+%d' % (x, y))
        self.attributes('-alpha', 1)
        self.deiconify()

    # this helps the programmer to determine the window width, which is set in ScrollbarFrame
    # print("I need width:", self.winfo_reqwidth())

    ################################
    #        BUTTON COMMANDS       #
    ################################

    def up_pressed(self, undo=True):
        if undo:
            self.undo_push()

        # get the selected rows
        sel = self.get_selected_rows()
        # if any are selected, move them up
        if sel:
            for entry in sel:
                # focus on a selected row, topmost first
                self.set_row_focus(int(entry.var_id.get()))
                # move it up
                self.move_up()
        else:
            self.move_up()

    def down_pressed(self, undo=True):
        if undo:
            self.undo_push()

        # this goes the same route as up_pressed() but the bottommost row must move first
        sel = self.get_selected_rows()
        if sel:
            for entry in reversed(sel):
                self.set_row_focus(int(entry.var_id.get()))
                self.move_down()
        else:
            self.move_down()

    def new_doc_pressed(self):
        self.parent.deiconify()

    def all_select(self):
        focused = self.focus_get()
        sel = self.get_selected_rows()
        if sel:
            self.deselect_all()
        else:
            self.select_all()
        self.all_checkbox.deselect()
        focused.focus_set()

    def heading_clicked(self, event):
        dia = ChangeTitleDialog(self)
        self.wait_window(dia.top)
        name, group = dia.name, dia.group
        if not dia.cancelled:
            self.var_heading.set(name + " med " + group)
        self.subject.name = name
        self.subject.group = group

    def info_clicked(self, event):
        dia = ChangeInfoDialog(self)
        self.wait_window(dia.top)
        teacher, school = dia.teacher, dia.school
        if not dia.cancelled:
            self.var_info.set(teacher + ", " + school)
        self.subject.teacher = teacher
        self.subject.school = school

    def day_clicked(self, event, var_day, lesson_id):
        # get the labels text
        day_old = var_day.get()

        # get the entry
        cl_entry = self.get_entry_at_id(lesson_id)

        # prepare the dialog text
        info_text = "Lektion # " + lesson_id + ", ändra dag från \"" + day_old + "\" till:"

        dia = ChangeDayDialog(self, info_text)
        self.wait_window(dia.top)

        # change only the clicked one if checkbox is unticked
        if dia.result == ChangeDayDialog.BUTTON_OK and not dia.change_all:
            self.undo_push()
            self.change_lesson_day(lesson_id, dia.var_day.get())

        # change them all, do not mark as odd since its a global change
        elif dia.result == ChangeDayDialog.BUTTON_OK:
            self.undo_push()
            for entry in self.lesson_entries:
                if entry.var_day.get() == day_old and entry.aorb() == cl_entry.aorb():
                    self.change_lesson_day(entry.var_id.get(), dia.var_day.get(), odd=False)

        # restore one if box is not ticked
        elif dia.result == ChangeDayDialog.BUTTON_RESTORE and not dia.change_all:
            self.undo_push()
            self.restore_lesson_day(lesson_id)

        # restore all if box is ticked
        elif dia.result == ChangeDayDialog.BUTTON_RESTORE and dia.change_all:
            self.undo_push()
            # print("Restoring all:", day_old)
            self.restore_lesson_days(day_old, cl_entry.aorb())

    def move_pressed(self):
        # prepare the text string in the message box
        message = ""
        current_index = self.get_row_focus()
        sel = self.get_selected_rows()

        # check if something is focused or selected
        if sel:
            message = "Flytta lektion #" + sel[0].var_id.get() + " ... #" + sel[-1].var_id.get() + " till # ..."
        elif current_index:
            message = "Flytta lektion #" + current_index + " till # ..."
        else:
            return

        # ask whereto
        target = tkinter.simpledialog.askinteger("Flytta", message, parent=self, minvalue=1,
                                                 maxvalue=len(self.lesson_entries))
        # When the user clicks cancel, do nothing
        if target is None:
            return
        elif self.lesson_locked(target):
            status = "ett prov." if self.lesson_entries[target - 1].var_test.get() else "inställd."
            tkinter.messagebox.showerror(title="Målet är låst", message="Lektionen du vill flytta till är " + status)

            # restore focus after warning box
            if current_index:
                current_index = int(current_index)
                self.set_row_focus(int(current_index))
            else:
                current_index = int(sel[0].var_id.get())
            return

        self.undo_push()

        # restore focus after dialog box
        if sel:
            current_index = int(sel[0].var_id.get())
        else:
            current_index = int(current_index)
            self.set_row_focus(int(current_index))

        moves = self.moves_between(current_index, target)
        # moving down
        if target > current_index:
            self.move_down_steps(moves)
        # moving up
        else:
            self.move_up_steps(moves)

        self.update()
        self.gather_sel()

    def bomb_pressed(self):
        sel = self.get_selected_rows()
        self.undo_push()

        if sel:
            for entry in reversed(sel):
                self.set_row_focus(int(entry.var_id.get()))
                self.remove_entry()
        else:
            self.remove_entry()


    def new_empty_pressed(self):
        self.undo_push()
        sel = self.get_selected_rows()
        if sel:
            for entry in sel:
                entry.entry_topic.focus_set()
                self.new_empty()
        else:
            self.new_empty()

        self.update_time_count()

    def clear_row(self, undo=False):
        # get the selected rows
        sel = self.get_selected_rows()

        if undo:
            self.undo_push()

        # if any are selected, clear them
        if sel:
            for entry in sel:
                entry.clear_entries()
        else:
            # else clear the focused row
            # get index of row to be moved
            target = self.get_row_focus()
            if target:
                target = int(target)
            else:
                return

            self.lesson_entries[target - 1].clear_entries()

    def remove_row(self, undo=False):

        if undo:
            self.undo_push()

        # clears a row or all selected rows and moves those below it up
        # to simulate a Excel-like delete row command
        # swap the empty row down to the bottom
        # get index of row to be moved

        # move it down
        # if several were selected
        sel = self.get_selected_rows()
        if sel:
            former_index = int(sel[0].var_id.get())
            for entry in reversed(sel):
                entry.clear_entries()
                self.set_row_focus(int(entry.var_id.get()))
                self.move_to_bottom()
            self.deselect_all()
            self.set_row_focus(former_index)

        else:
            self.clear_row()
            former_index = self.get_row_focus()
            if former_index:
                former_index = int(former_index)

            else:
                return
            self.move_to_bottom()
            self.set_row_focus(former_index)



    ################################
    #       MENUBAR COMMANDS       #
    ################################

    def export_excel(self, layout="tor"):
        for entry in self.lesson_entries:
            entry.update_model()

        # ask for path to save xlsx

        xpath = tk.filedialog.askdirectory()

        if not xpath:
            return

        xname = self.subject.name + " " + self.subject.group + " " + self.subject.teacher + ".xlsx"

        if layout == "tor":
            sx.export_subject(self.subject, xpath)
        elif layout == "mattias":
            sxm.export_subject(self.subject, xpath)
        else:
            tkinter.messagebox.showerror(title="Ogiltig parameter", message="export_excel(): ogiltig parameter: "+layout)
            return

        tkinter.messagebox.showinfo(title="Export klar", message="Planeringen exporterades till " + xpath +"/"+ xname,
                                    master=self)

    def gather_sel(self, undo=False):
        if undo:
            self.undo_push()

        sel = self.get_selected_rows()
        if not sel:
            return
        top_e = sel[0]
        top_id = int(top_e.var_id.get())

        # deselect all and move one at a time to correct pos
        self.deselect_all()

        counter = 1
        for entry in sel[1:]:
            e_id = int(entry.var_id.get())
            self.set_row_focus(e_id)
            d = self.moves_between(e_id, top_id)
            # print("gather_sel(): #", e_id, "will move", d, "steps")
            self.move_up_steps(d - counter, undo=False)
            self.update()
            counter += 1

        self.set_row_focus(top_id)

    def merge_command(self):
        sel_rows = self.get_selected_rows()

        if len(sel_rows)<2:
            tkinter.messagebox.showerror(title="Fel", message="Markera två eller fler lektioner att slå ihop.",
                                         parent=self)
            return

        self.undo_push()

        # do the work
        intlids = [int(x.var_id.get()) for x in sel_rows]
        self.merge_rows(tuple(intlids))

    def create_new_week(self, scroll=True):
        self.undo_push()

        # create lessons for the week according to
        last_week = int(self.lesson_entries[-1].week())
        last_ab = self.lesson_entries[-1].aorb()
        new_ab = ""

        days = []
        if not last_ab:
            days = self.subject.lesson_days
        elif last_ab == "A":
            days = self.subject.lesson_days_b
            new_ab = "B"
        else:
            days = self.subject.lesson_days_a
            new_ab = "A"

        # print("create_new_week(): new week is", days)

        for day in days:
            # wrap weeks after week 51 (51 --> 2)
            if last_week == 51:
                last_week = 1

            lid = 1 + int(self.lesson_entries[-1].var_id.get()) if self.lesson_entries else 1

            new_lesson = Lesson(last_week + 1, day, is_odd=False, id=lid, week_ab=new_ab)
            new_entry = LessonEntry(new_lesson, self.lessons_frame, self.update_time_count, _font=BASE_FONT,
                                    _bg=BG_COLOR, _weekfont=WEEK_FONT, _idfont=ID_FONT, _dayfont=DAY_FONT,
                                    _relief=ENTRY_RELIEF)
            new_entry.var_duration.set(self.prob_org_duration(new_entry))
            new_entry.original_duration = self.prob_org_duration(new_entry)
            self.lesson_entries.append(new_entry)

            # grid it, add to the bottom of the rows
            new_entry.grid(len(self.lesson_entries) + 2, 1)
            self.set_entry_bindings(new_entry)

        self.update_idletasks()
        self.update_time_count()

        if scroll:
            self.lesson_entries[-1].entry_topic.focus_set()
            self.frame.scroll_to("1.0")

    def create_odd_lesson(self):
        # TODO: it tags the bottom lesson as odd and doesnt remove that property. Do this:
        # save the status of the bottom and restore it before the function returns.
        # I've fixed the issue. Its cause was in the swap method, and the property odd wasnt swapped correctly.

        ## well, it works, but theres a problem somewhere in swap or move functions that set or desets odd (on adjacent
        ## to odd lessons (below?)) and cancelled on the top item.
        # last_odd = self.lesson_entries[-1].odd

        dia = NewLessonDialog(self, message="Skapa ny lektion. Ange när.")
        self.wait_window(dia.top)

        if not dia.cancelled:
            # Find out if its A or B week, add the letter to the week
            found = False
            ab = ""
            for entry in self.lesson_entries:
                # print("create_odd_lesson(): entry.week() ==", entry.week(), "dia.week ==", dia.week)
                if int(entry.week()) == int(dia.week):
                    ab = entry.aorb()
                    found = True
                    # print("create_odd_lesson(): new lesson is", ab, "week")

            if not found:
                ab = tkinter.simpledialog.askstring(title="Veckotyp", prompt="Ange om veckan är A eller B\n" +
                                                    "Avbryt om det inte spelar någon roll", parent=self)

                if ab is None:
                    ab = ""
                elif ab not in ("A", "B"):
                    tkinter.messagebox.showerror(title="Fel veckotyp", message="Ange A eller B som veckotyp." +
                                                                               " Pröva igen.")
                    return

            # due to a bug in move_up(), if the topmost lesson is locked, the new entry wrongly goes
            # underneath it despite being supposed to go over. Fix by temporarily unlocking it before move_to_top() is called.
            # The original values are stored here and then restored.
            top_item = self.lesson_entries[0]
            top_c = top_item.var_cancelled.get()
            top_t = top_item.var_test.get()
            top_item.var_test.set(False)
            top_item.var_cancelled.set(False)

            # Create a new lesson entry and att it to the list
            new_lesson = Lesson(dia.week, dia.day, is_odd=True,
                                id=1 + int(self.lesson_entries[-1].var_id.get()) if self.lesson_entries else 1,
                                week_ab=ab.upper())
            new_entry = LessonEntry(new_lesson, self.lessons_frame, self.update_time_count, move_all=True,
                                    _font=BASE_FONT, _relief=ENTRY_RELIEF,
                                    _bg=BG_COLOR, _weekfont=WEEK_FONT, _idfont=ID_FONT, _dayfont=DAY_FONT)
            self.lesson_entries.append(new_entry)

            # grid it, color it, add to the bottom of the rows
            new_entry.label_day.config(fg=Constants.ODD_COLOR)
            new_entry.grid(len(self.lesson_entries) + 2, 1)
            self.set_entry_bindings(new_entry)
            self.update_idletasks()
            self.update()

            # set the focus on the new lesson at the bottom, so that it can me moved up
            self.set_row_focus(int(new_entry.var_id.get()))

            # check if it wraps
            wrap = False
            wrap_week = 0

            for i in range(len(self.lesson_entries) - 2):
                # if an entry below has a lower week number, then it wraps. don't count the last one (newly added)
                if int(self.lesson_entries[i].week()) > int(self.lesson_entries[i + 1].week()):
                    wrap = True
                    wrap_week = int(self.lesson_entries[i].week())
                    break
            # print("Weeks wrap at week " + str(wrap_week) if wrap else "Weeks do not wrap")

            # define the terms which determines if a row should go to top or bottom.
            term_ht = range(29, 53)  # weeks 29-52
            term_vt = range(1, 29)  # weeks 2-28

            if wrap:
                # if it wraps: move up to wrap week if the formerly last rows week is less than target
                # then proceed as usual

                # case where row should be added to the top - its less than the uppermost and in HT
                if (dia.week in term_ht) and (dia.week < int(self.lesson_entries[0].week())):
                    self.move_to_top()
                # case where it stays on the bottom
                elif (dia.week in term_vt) and (dia.week > int(self.lesson_entries[-2].week())):
                    pass
                # if its going to the upper side of the wrap
                elif dia.week > int(self.lesson_entries[-2].week()):

                    # move it to the wrap week
                    self.move_to_wrap(wrap_week)

                    # ...then move it upwards to the correct week by comparing the row above to the target dia.week
                    self.move_to_correct_week_pos(dia.week)

                    # ...then move it upwards to the correct day by comparing it to the one above
                    self.move_to_correct_day_pos()

                # if its going to the lower side of the wrap
                else:
                    # move it upwards to the correct week by comparing the row above to the target dia.week
                    self.move_to_correct_week_pos(dia.week)

                    # ...then move it upwards to the correct day by comparing it to the one above
                    self.move_to_correct_day_pos()

            # when there's no wrap three things can happen
            else:
                # case where all lessons are HT
                if int(self.lesson_entries[0].week()) in term_ht and int(
                        self.lesson_entries[-2].week()) in term_ht:
                    # put entry belonging to vt where it belongs
                    if dia.week in term_vt:
                        pass
                    # if its less than all others, to the top it goes
                    elif dia.week < int(self.lesson_entries[0].week()):
                        self.move_to_top()
                    # last case where's there no wrap and the new entry just has to me moved up to correct position
                    else:
                        self.move_to_correct_week_pos(dia.week)
                        self.move_to_correct_day_pos()
                # case where all lessons are VT (guaranteed since theres no wrap and they're not in HT
                else:
                    # if it belongs to ht, move it there - to the top
                    if dia.week in term_ht:
                        self.move_to_top()
                    # pull it to the top if its smallest and in vt
                    elif dia.week < int(self.lesson_entries[0].week()):
                        self.move_to_top()
                    # keep it at the bottom if its the largest
                    elif dia.week > int(self.lesson_entries[-2].week()):
                        pass
                    # last case where's there no wrap and the new entry just has to me moved up to correct position
                    else:
                        self.move_to_correct_week_pos(dia.week)
                        self.move_to_correct_day_pos()

            # mark all entries move_all = False
            for entry in self.lesson_entries:
                entry.move_all = False

            # restore the top items state
            top_item.var_cancelled.set(top_c)
            top_item.var_test.set(top_t)

            # self.lesson_entries[-1].odd = last_odd
            # self.lesson_entries[-1].refresh_color()
            self.update_time_count()
            self.update()
            self.update_idletasks()


    def swap_ab_on_focused_week(self):
        foc_lesson = self.get_focused_entry()
        week = ""
        if foc_lesson:
            week = foc_lesson.var_week.get()
        else:
            return

        lessons = self.lessons(week)

        for lesson in lessons:
            self.swap_ab_on_lesson(lesson)


    def swap_ab_on_lesson(self, lesson: LessonEntry):
        week = lesson.var_week.get()
        if week[-1] == "A":
            lesson.var_week.set(week[0:-1] + "B")
        elif week[-1] == "B":
            lesson.var_week.set(week[0:-1] + "A")
        else:
            return

    # returns a tuple of lessons that match week
    def lessons(self, week: str) -> tuple:
        found_lessons = []
        for lesson in self.lesson_entries:
            if lesson.var_week.get() == week:
                found_lessons.append(lesson)
        return tuple(found_lessons)




    ################################
    #      KEY BINDING FUNCS       #
    ################################

    def scrolling(self, event):
        self.frame.canvas.yview_scroll(int(-1*event.delta/SCR_SPEED), "units")

    def scrolling_linux(self, event):
        if event.num == 4:
            # print("<4> (up) pressed, delta =" ,event.delta)
            self.frame.canvas.yview_scroll(1, "units")
        elif event.num == 5:
            # print("<5> (down) pressed, delta =", event.delta)
            self.frame.canvas.yview_scroll(-1, "units")

    # key up moves focus to the entry above
    def key_up(self, event, f_entry):
        entry_hi = self.get_focused_entry()
        entry_lo = self.get_entry_at_id(int(entry_hi.var_id.get()) - 1)

        if not entry_lo:
            return

        hi1, hi2, hi3, hi4 = entry_hi.get_entry_widgets()
        lo1, lo2, lo3, lo4 = entry_lo.get_entry_widgets()

        if f_entry is hi1:
            lo1.icursor(tkinter.END)
            lo1.focus_set()
        elif f_entry is hi2:
            lo2.icursor(tkinter.END)
            lo2.focus_set()
        elif f_entry is hi3:
            lo3.icursor(tkinter.END)
            lo3.focus_set()
        else:
            lo4.icursor(tkinter.END)
            lo4.focus_set()

        self.scroll_fit(lo1, 1)

    # key down moves focus to the entry below
    def key_down(self, event, f_entry):
        entry_lo = self.get_focused_entry()
        entry_hi = self.get_entry_at_id(int(entry_lo.var_id.get()) + 1)

        if not entry_hi:
            return

        hi1, hi2, hi3, hi4 = entry_hi.get_entry_widgets()
        lo1, lo2, lo3, lo4 = entry_lo.get_entry_widgets()

        if f_entry is lo1:
            hi1.icursor(tkinter.END)
            hi1.focus_set()
        elif f_entry is lo2:
            hi2.icursor(tkinter.END)
            hi2.focus_set()
        elif f_entry is lo3:
            hi3.icursor(tkinter.END)
            hi3.focus_set()
        else:
            hi4.icursor(tkinter.END)
            hi4.focus_set()

        self.scroll_fit(hi1, 1)

    def scroll_fit(self, widget, nrows):
        # scrolls up or down nrows number of scroll units to keep focused entry visible when arrow up or down in pressed
        wy = widget.winfo_rooty()
        first1, first2, first3, first4 = self.lesson_entries[0].get_entry_widgets()

        # scroll to absolute top if widget is #1
        if widget is first1 or widget is first2 or widget is first3 or widget is first4:
            self.frame.scroll_to("0.0")
        # scroll up if widget is hidden from view at the top
        elif wy <= self.frame.vsb.winfo_rooty():
            self.frame.canvas.yview_scroll(-1*nrows, "units")
        # scroll down if widget is hidden from view below
        elif wy > self.frame.vsb.winfo_rooty()+self.frame.vsb.winfo_height()-widget.winfo_height():
            self.frame.canvas.yview_scroll(nrows, "units")

    #####################################
    #   Controller functions for  GUI   #
    #####################################

    # creates an undo object, ie a value copy of all lessons before edit
    def undo_object(self) -> tuple:
        u_obj = []
        for entry in self.lesson_entries:
            # saving info

            u_obj.append((entry.var_week.get(),         #0
                          entry.aorb(),                 #1
                          entry.var_day.get(),          #2
                          entry.var_id.get(),           #3
                          entry.var_topic.get(),        #4
                          entry.entry_pages.get(),      #5
                          entry.var_assignment.get(),   #6
                          entry.var_link.get(),         #7
                          entry.var_test.get(),         #8
                          entry.var_cancelled.get(),    #9
                          entry.var_duration.get(),     #10
                          entry.odd,                    #11
                          entry.original_day,           #12
                          entry.original_duration))     #13
        return tuple(u_obj)

    # pushes an undo object onto the undo stack
    def undo_push(self):
        # saves up to MAX_UNDO undo states. Delete the oldest if undo_buffer is full
        if len(self.undo_buffer) >= MAX_UNDO:
            self.undo_buffer.pop(Constants.MAX_UNDO-1)
        self.undo_buffer.insert(0, self.undo_object())


    # restores the state before an action
    def undo_restore(self):
        if not self.undo_buffer:
            # print("undo_restore(): cannot undo: buffer is empty")
            return

        # fetch the previous state
        r_obj = self.undo_buffer[0]

        # determine if new rows need to be added to fit the whats restored. If so, create weeks to make it fit
        if len(r_obj) > len(self.lesson_entries):
            while len(r_obj) > len(self.lesson_entries):
                self.create_new_week(scroll=False)

        # restore all entries from undo object
        i = 0
        for row in r_obj:
            # fill in from r_obj
            self.lesson_entries[i].var_week.set(row[0])         #0
            self.lesson_entries[i].ab_week = row[1]             #1
            self.lesson_entries[i].var_day.set(row[2])          #2
            self.lesson_entries[i].var_id.set(row[3])           #3
            self.lesson_entries[i].var_topic.set(row[4])        #4
            self.lesson_entries[i].var_pages.set(row[5])        #5
            self.lesson_entries[i].var_assignment.set(row[6])   #6
            self.lesson_entries[i].var_link.set(row[7])         #7
            self.lesson_entries[i].var_test.set(row[8])         #8
            self.lesson_entries[i].var_cancelled.set(row[9])    #9
            self.lesson_entries[i].var_duration.set(row[10])    #10
            self.lesson_entries[i].odd = row[11]                #11
            self.lesson_entries[i].original_day = row[12]       #12
            self.lesson_entries[i].original_duration = row[13]  #13
            self.lesson_entries[i].refresh_color()
            i += 1

        for j in range(i, len(self.lesson_entries)):
            self.lesson_entries[j].clear_entries()

        # remove the restored entry from the undo buffer
        self.undo_buffer.pop(0)

        self.update_time_count()


    def donothing(self):
        tkinter.messagebox.showinfo(title="Information", message="Funktionen är inte implementerad ännu.", parent=self)


    def update_gui(self):
        pass

    def update_model(self):
        for entry in self.lesson_entries:
            entry.update_model()

    def change_lesson_day(self, lesson_id, day_to, odd=True):
        # find the correct lesson entry
        for entry in self.lesson_entries:
            if entry.var_id.get() == lesson_id:
                if day_to == entry.original_day:
                    self.restore_lesson_day(lesson_id)
                    break
                else:
                    entry.var_day.set(day_to)
                    if odd:
                        entry.odd = True
                        entry.label_day.configure(fg=Constants.ODD_COLOR)
                    break

    def restore_lesson_day(self, lesson_id):
        for entry in self.lesson_entries:
            if entry.var_id.get() == lesson_id:
                entry.var_day.set(entry.original_day)
                entry.odd = False
                entry.label_day.configure(fg="black")
                break

    def restore_lesson_days(self, day: str, weekab: str):
        for entry in self.lesson_entries:
            if entry.var_day.get() == day and entry.ab_week == weekab:
                entry.var_day.set(entry.original_day)
                entry.odd = False

    def lesson_locked(self, l_id) -> bool:
        entry = self.get_entry_at_id(l_id)
        if entry is None:
            return True
        return entry.var_test.get() or entry.var_cancelled.get()

    def focus_down(self, event):
        try:
            self.set_row_focus(int(self.get_row_focus()) + 1)
            self.scroll_fit(self.get_focused_entry().entry_topic, 1)
        except:
            pass

    def select_multi(self, event, clicked_entry, all=False):
        # selects all entries between two endpoints when shift is held (all=True)
        # selects all non locked entries between endpoints when control is held (all=False)
        if len(self.get_selected_rows()) > 1:
            return

        prev_id = int(self.get_selected_rows()[0].var_id.get())
        new_id = int(clicked_entry.var_id.get())

        index_lo = new_id if new_id < prev_id else prev_id
        index_hi = new_id if new_id > prev_id else prev_id

        # select entries between the clicked index and the prev. selected
        for i in range(index_lo + 1, index_hi):
            entry = self.get_entry_at_id(i)
            if all:
                entry.checkbox_selected.invoke()
            elif not (entry.var_cancelled.get() or entry.var_test.get()):
                entry.checkbox_selected.invoke()

    def on_close(self):
        # print("on_close(): Asking about quit")
        result = False
        if self.seconds_since_save >= 10:
            result = tkinter.messagebox.askyesnocancel("Spara?", "Vill du spara innan du avslutar?", parent=self)

        # cancel pressed, just return to the program
        if result is None:
            return
        # yes pressed
        elif result:
            self.save_csv()
            if self.parent:
                self.parent.deiconify()
                self.destroyed = True
                self.destroy()
            else:
                self.destroyed = True
                self.destroy()
        # no pressed,
        else:
            # If there are still windows open, display them
            if self.parent and not self.parent.destroyed:
                self.parent.deiconify()
                self.destroyed = True
                self.destroy()
            # If self is last window opened, show the InfoWin
            else:
                self.destroyed = True
                self.destroy()
                self.parent.deiconify()

    def set_entry_bindings(self, entry):
        entry.label_day.bind("<Button-1>", lambda event, v=entry.var_day,
                             lid=entry.var_id.get(): self.day_clicked(event, v, lid))
        entry.label_duration.bind("<Button-1>", lambda v, e=entry: self.change_duration(v, e))
        entry.checkbox_selected.bind("<Shift-1>", lambda v, e=entry: self.select_multi(v, e, all=True))
        entry.checkbox_selected.bind("<Control-1>", lambda v,e=entry: self.select_multi(v, e))
        entry.entry_topic.bind("<Up>", lambda v, e=entry.entry_topic: self.key_up(v, e))
        entry.entry_pages.bind("<Up>", lambda v, e=entry.entry_pages: self.key_up(v, e))
        entry.entry_assignment.bind("<Up>", lambda v, e=entry.entry_assignment: self.key_up(v, e))
        entry.entry_link.bind("<Up>", lambda v, e=entry.entry_link: self.key_up(v, e))
        entry.entry_topic.bind("<Down>", lambda v, e=entry.entry_topic: self.key_down(v, e))
        entry.entry_pages.bind("<Down>", lambda v, e=entry.entry_pages: self.key_down(v, e))
        entry.entry_assignment.bind("<Down>", lambda v, e=entry.entry_assignment: self.key_down(v, e))
        entry.entry_link.bind("<Down>", lambda v, e=entry.entry_link: self.key_down(v, e))

    def change_duration(self, event, entry):
        # tkinter.simpledialog.askinteger("Ändra tid", "Ändra lektionens längd till:", parent=self, minvalue=0)
        # prepare the dialog text

        dia = ChangeDurationDialog(self, "Lektion # " + entry.var_id.get() + ", ändra längden till:")
        self.wait_window(dia.top)

        # change only the clicked one if checkbox is unticked
        if dia.result == ChangeDurationDialog.BUTTON_OK and not dia.change_all:
            self.undo_push()
            entry.var_duration.set(dia.time)
            entry.original_duration = dia.time
            self.update_time_count()

        # change them all, but change only if a or b week and day match
        elif dia.result == ChangeDurationDialog.BUTTON_OK:
            self.undo_push()

            for row in self.lesson_entries:
                if row.var_day.get() == entry.var_day.get() and row.aorb() == entry.aorb() and\
                        row.var_test.get() == row.var_cancelled.get():
                    row.var_duration.set(dia.time)
                    row.original_duration = dia.time

            self.update_time_count()

    def update_time_count(self):
        tdur = 0

        # calculate hours and minutes of lesson time
        for entry in self.lesson_entries:
            if entry is None:
                continue
            # if cancelled and test are checked, lesson is just locked
            elif entry.var_test.get() and entry.var_cancelled.get():
                tdur += int(entry.var_duration.get())
            elif not self.lesson_locked(int(entry.var_id.get())):
                tdur += int(entry.var_duration.get())

        th = int(tdur / 60)
        tm = tdur - th * 60

        # print("Hours:", th, "minutes:", tm)
        self.var_time.set("Lektionstid: " + str(th) + " h " + str(tm) + " min")

        # update the variable holding the total minute count
        self.total_minutes = tdur

    def create_lesson_entries(self):
        row = 3
        col = 1
        for lesson in self.subject.all_lessons:
            entry = LessonEntry(lesson, self.lessons_frame, self.update_time_count, _relief=ENTRY_RELIEF,
                                _dayfont=DAY_FONT,
                                _font=BASE_FONT, _bg=BG_COLOR, _idfont=ID_FONT, _weekfont=WEEK_FONT)
            entry.grid(row, col, _padx=1)
            self.set_entry_bindings(entry)
            self.lesson_entries.append(entry)

            # if loaded from csv, transfer the loaded data from the model to GUI
            entry.update_GUI()
            row += 1

    def get_entry_at_id(self, entry_id) -> LessonEntry:
        if int(entry_id) <= len(self.lesson_entries) and int(entry_id)>0:
            return self.lesson_entries[int(entry_id) - 1]
        else:
            return None

    # Find the index of the row thats in focus
    def get_row_focus(self) -> str:
        focused = self.focus_get()
        # Search all entries/textentryfields for which one is in focus
        for entry in self.lesson_entries:
            entry_one, entry_two, entry_three, entry_four = entry.get_entry_widgets()
            # when it's found, return its ID
            if focused is entry_one or focused is entry_two or focused is entry_three or focused is entry_four:
                return entry.var_id.get()
        # if no row is in focus, return None
        return None

    # return the LessonEntry of the row thats in focus
    def get_focused_entry(self) -> tk.Entry:
        focused = self.focus_get()

        # Search all entries/textentryfields for which one is in focus
        for entry in self.lesson_entries:
            entry_one, entry_two, entry_three, entry_four = entry.get_entry_widgets()

            # when it's found, return it
            if focused is entry_one or focused is entry_two or focused is entry_three or focused is entry_four:
                return entry

        # if no row is in focus, return None as an "error"
        return None

    def set_row_focus(self, index: int):
        try:
            self.lesson_entries[index - 1].entry_topic.focus_set()
        # print("set_row_focus(): focus is on #", self.lesson_entries[index - 1].var_id.get())
        except IndexError:
            # print("set_row_focus(): index error on index:", index)
            pass

    def remove_entry(self):
        # print("len(self.lesson_entries) =", len(self.lesson_entries))
        foc_id = self.get_row_focus()
        # print("remove_entry(): removing lesson:", foc_id)

        if not foc_id:
            return

        # remove it from the GUI
        self.lesson_entries[int(foc_id)-1].destroy()

        # remove it from lesson_entries
        self.lesson_entries.pop(int(foc_id)-1)
        # print("len(self.lesson_entries) =", len(self.lesson_entries))
        self.reindex()

        self.update_time_count()

        self.set_row_focus(int(foc_id))

        for entry in self.lesson_entries:
            entry.move_all = False

    def reindex(self):
        # fixes id:s of self.lesson_entries, making them go from 1..n
        i = 1
        for entry in self.lesson_entries:
            entry.var_id.set(str(i))
            i+=1

    # removes an entry entirely, leaving the GUI with one entry less
    def old_remove_entry(self):
        # move it to the bottom, the whole row
        focused_entry = self.get_focused_entry()

        if focused_entry is None:
            return
        else:
            # tag all as "move all" to move everything up one step
            for entry in self.lesson_entries:
                entry.move_all = True

        current_index = int(self.get_row_focus())
        former_index = int(self.get_row_focus())
        target = len(self.lesson_entries)

        while current_index < target:
            self.move_down()
            current_index += 1

        # remove it from the GUI
        self.lesson_entries[-1].destroy()

        # remove it from lesson_entries
        del self.lesson_entries[-1]

        # restore focus if the list is not empty
        if not self.lesson_entries:
            return
        elif former_index > int(self.lesson_entries[-1].var_id.get()):
            self.set_row_focus(former_index - 1)
        else:
            self.set_row_focus(former_index)

        for entry in self.lesson_entries:
            entry.move_all = False

            if entry.var_cancelled.get():
                entry.color_row(CANCELLED_COLOR)
            elif entry.var_test.get():
                entry.color_row(TEST_COLOR)
            else:
                entry.color_row(BG_COLOR)

    def get_selected_rows(self) -> tuple:
        sel_entries = []
        for entry in self.lesson_entries:
            if entry.var_selected.get():
                sel_entries.append(entry)
        return tuple(sel_entries)

    def select_all(self):
        for entry in self.lesson_entries:
            if not entry.var_selected.get():
                entry.checkbox_selected.invoke()

    def deselect_all(self):
        for entry in self.lesson_entries:
            if entry.var_selected.get():
                entry.checkbox_selected.invoke()

    def move_down(self):
        # get index of row to be moved
        index_lo = self.get_row_focus()
        if index_lo:
            index_lo = int(index_lo)
        else:
            return

        # Do bounds check before swap
        if index_lo >= len(self.lesson_entries):
            return

        # if entry is flagged as move_all, disregard that cancelled and test are stationary
        if self.get_focused_entry().move_all:
            self.swap_rows(index_lo, index_lo + 1)
            self.set_row_focus(index_lo + 1)
            return

        # find the one below to swap to, jump if test and cancelled
        steps = 1
        index_hi = index_lo

        while self.lesson_entries[index_hi + steps - 1].var_cancelled.get() or \
                self.lesson_entries[index_hi + steps - 1].var_test.get():

            # Check out of bounds
            if index_hi + steps >= len(self.lesson_entries):
                return

            steps += 1

        index_hi = index_lo + steps

        # swap them
        self.swap_rows(index_hi, index_lo)

        # Change focus so that it tracks the row that moved down
        self.set_row_focus(index_hi)

    def move_up(self):
        # get index of row to be moved
        index_hi = self.get_row_focus()

        if index_hi:
            index_hi = int(index_hi)
        else:
            return

        index_hi = int(self.get_row_focus())

        # Do bounds check before swap
        if index_hi == 1:
            return

        # if entry is flagged as move_all, disregard that cancelled and test are stationary
        if self.get_focused_entry().move_all:
            # print("move_up(): #", str(index_hi), "---> #", str(index_hi-1))
            self.swap_rows(index_hi, index_hi - 1)
            self.set_row_focus(index_hi - 1)
            return

        # find the one above to swap to, ignore test and cancelled
        steps = 1
        index_lo = index_hi

        while self.lesson_entries[index_lo - steps - 1].var_cancelled.get() or \
                self.lesson_entries[index_lo - steps - 1].var_test.get():
            steps += 1
        index_lo = index_hi - steps

        # swap them if the index doesnt underflow
        if index_lo > 0:
            self.swap_rows(index_hi, index_lo)
            # Change focus so that it tracks the row that moved up
            self.set_row_focus(index_lo)

    def new_empty(self):
        # get index of row to be moved
        target_id = self.get_row_focus()

        # if its None, nothings in focus and we abort
        # else convert it to int
        if target_id:
            target_id = int(target_id)
        else:
            return

        # Create a new week if last row is not empty
        if not self.lesson_entries[-1].empty():
            # print("Lesson #", self.lesson_entries[-1].var_id.get(), "is empty:", self.lesson_entries[-1].empty())
            self.create_new_week(scroll=False)
        elif self.get_row_focus() == self.lesson_entries[-1].var_id.get():
            self.create_new_week(scroll=True)

        # set focus on the last row
        self.lesson_entries[-1].entry_topic.focus_set()

        # swap the empty row upwards until at correct index.
        current_index = len(self.lesson_entries) - 1
        while current_index > target_id:
            self.move_up()
            current_index = int(self.get_row_focus())

    def move_to_wrap(self, wrap_week):
        while int(self.lesson_entries[int(self.get_row_focus()) - 2].week()) != wrap_week:
            self.move_up()

    def move_to_correct_week_pos(self, week):
        # assuming the entry is already on the correct side of the wrap
        # move it upwards to the correct week by comparing the row above to the target dia.week
        while int(self.lesson_entries[int(self.get_row_focus()) - 2].week()) > week:
            self.move_up()

            # if it gets to the top, abort
            if self.get_row_focus() == 1 or self.get_row_focus() is None:
                return

    def move_to_correct_day_pos(self):
        # move it upwards to the correct day by comparing it to the one above
        # assumes all entrys are flagged move_all=True

        # store variables that are used below for readability
        fentry = self.get_focused_entry()
        fid = int(fentry.var_id.get())
        fday = fentry.var_day.get().lower()
        fweek = int(fentry.week())

        # move up entry while day and week is less
        while (DAY_COMP[fday] < DAY_COMP[self.lesson_entries[fid - 2].var_day.get()]) and \
                (fweek <= int(self.lesson_entries[fid - 2].week())):

            if fid == 1 or self.get_row_focus() is None:
                return

            self.move_up()
            fentry = self.get_focused_entry()
            fid = int(fentry.var_id.get())
            fday = fentry.var_day.get()
            fweek = int(fentry.week())

    def move_to_top(self):
        # find the id of the topmost item thats not cancelled and not a test
        top_free_id = 0
        for entry in self.lesson_entries:
            if (not entry.var_test.get()) and (not entry.var_cancelled.get()):
                top_free_id = int(entry.var_id.get())
                break

        # move up to that
        while int(self.get_row_focus()) > top_free_id:
            self.move_up()

    def move_to_bottom(self):
        # find the id of the topmost item that's not cancelled and not a test
        last_free_id = 0
        for entry in reversed(self.lesson_entries):
            if (not entry.var_test.get()) and (not entry.var_cancelled.get()):
                last_free_id = int(entry.var_id.get())
                break

        while int(self.get_row_focus()) < last_free_id:
            self.move_down()


    def days_of_week(self, week_nr) -> tuple:
        days = []
        # append all days of week week_nr to the array
        for entry in self.lesson_entries:
            if int(entry.week()) == week_nr and not entry.odd:
                days.append(entry.var_day.get())

        # return an empty array if the week isn't present
        # else return one instance of every day (a set of the days)
        return tuple(days)


    def moves_between(self, i, j) -> int:
        # swap up or down?

        # make i the least
        if i > j:
            i, j = j, i

        # entries between i and j including them
        journey = self.lesson_entries[i - 1:j - 1]
        counter = 0

        # print("moves_between(): journey is", len(journey), "entries")

        # count the cancelled and test
        for entry in journey:
            if entry.var_cancelled.get() or entry.var_test.get():
                counter += 1

        # print("moves_between(): found", counter, "locked lessons in journey")
        # print("moves_between():", j - i - counter, "moves are needed")

        # subtract the cancelled and tests from the number of steps between j and i.
        return j - i - counter

    def move_up_steps(self, steps, undo=True):
        if undo:
            self.undo_push()

        for i in range(steps):
            self.up_pressed(undo=False)

    def move_down_steps(self, steps, undo=True):
        if undo:
            self.undo_push()

        for i in range(steps):
            self.down_pressed(undo=False)

    def _move_to(self, target):
        current_index = int(self.get_row_focus())

        # if nothing is in focus, return
        if current_index < 1:
            return

        # after the dialog, focus will be lost, so let's restore focus
        self.set_row_focus(current_index)

        # swap up or down?
        if target > current_index:
            # print("move_to(): moving down")
            journey = self.lesson_entries[current_index - 1:target - 1]
            counter = 0
            for entry in journey:
                if not entry.var_cancelled.get() and not entry.var_test.get():
                    counter += 1
            # print("move_to(): will do", counter, "moves")
            for i in range(counter):
                self.move_down()
        elif target < current_index:
            # print("move_to(): moving up")
            journey = self.lesson_entries[target - 1:current_index - 1]
            counter = 0
            for entry in journey:
                if not entry.var_cancelled.get() and not entry.var_test.get():
                    counter += 1
            # print("move_to(): will do", counter, "moves")
            for i in range(counter):
                self.move_up()

    def merge_rows(self, lids: tuple):
        # read the contents of the rows of the ids in lids, save that to four new strings from the contents
        # separated by comma

        mrg_topic = ""
        mrg_pages = ""
        mrg_assignment = ""
        mrg_link = ""

        # merge the text fields
        for lid in lids:
            entry = self.get_entry_at_id(lid)
            spacer = "" if lid==lids[-1] else "; "
            mrg_topic += (entry.var_topic.get() + spacer if entry.var_topic.get().strip() else "")
            mrg_pages += (entry.var_pages.get() + spacer if entry.var_pages.get().strip() else "")
            mrg_assignment += (entry.var_assignment.get() + spacer if entry.var_assignment.get().strip() else "")
            mrg_link += (entry.var_link.get() + spacer if entry.var_link.get().strip() else "")

        # set the top row to those strings, but trim ; from them first
        target = self.get_entry_at_id( lids[0] )
        target.var_topic.set(self.trim_tr_sym(mrg_topic, ";"))
        target.var_pages.set(self.trim_tr_sym(mrg_pages, ";"))
        target.var_assignment.set(self.trim_tr_sym(mrg_assignment, ";"))
        target.var_link.set(self.trim_tr_sym(mrg_link, ";"))

        # remove unwanted non merged entries (keep the top one containing the others)
        self.deselect_all()
        for lid in reversed(lids[1:]):
            if lid != lids[0]:
                self.set_row_focus(int(lid))
                self.remove_row()


    # trims all occurences of the leading or trailing symbol from tr_str
    def trim_tr_sym(self, tr_str: str, symbol: str) -> str:

        if tr_str == symbol:
            return ""
        elif not tr_str:
            return ""

        while tr_str[-1] == symbol:
            tr_str = tr_str[:-1]

        while tr_str[0] == symbol:
            tr_str = tr_str[1:]

        return tr_str

    def split_row(self):
        # fetch the lessons to be modified, and their id:s
        fid = int(self.get_row_focus())
        fentry = self.get_focused_entry()

        # split the data in the four entry widgets at char ';'
        spltopic = fentry.var_topic.get().split(";")
        splpages = fentry.var_pages.get().split(";")
        splassignment = fentry.var_assignment.get().split(";")
        spllink = fentry.var_link.get().split(";")

        # if four fields produce less than five new fields of data, there's nothing to split
        if len(spltopic)+len(splpages)+len(splassignment)+len(spllink) < 5:
            tkinter.messagebox.showerror(title="Delningsfel", message="Kunde inte dela lektionen eftersom den inte "+
                                                                      "innehåller delbar text.\n" + "Avgränsa delbart"+
                                                                      " lektionsinnehåll med semikolon.",
                                         parent=self)
            return

        self.undo_push()

        # find out how many new lessons it will split to and create that many empty
        nwnum = max(len(spltopic), len(splpages), len(splassignment), len(spllink))
        for i in range(nwnum-1):
            self.new_empty()

        # create a filler array with empty elements, which extends the spl-lists to avoid index out of bounds
        filler = ["" for i in range(nwnum)]
        spltopic += filler
        splpages += filler
        splassignment += filler
        spllink += filler
        # print(spltopic)
        # print(splpages)
        # print(splassignment)
        # print(spllink)

        # fill the empty rows with the splitted data
        free_ids = self.map_next_n_unlocked(nwnum, fid)
        # print(free_ids)
        counter = 0
        for i in free_ids:
            row = self.lesson_entries[i-1]
            row.var_topic.set(spltopic[counter].strip())
            row.var_pages.set(splpages[counter].strip())
            row.var_assignment.set(splassignment[counter].strip())
            row.var_link.set(spllink[counter].strip())
            counter += 1

    def map_next_n_unlocked(self, n: int, id_from: int) -> tuple:
        free_found = 0
        counter = 0
        free_ids = []

        while free_found < n:
            if self.lesson_locked(id_from+counter):
                counter += 1
            else:
                free_ids.append(id_from+counter)
                counter += 1
                free_found += 1

        return tuple(free_ids)

    def dupl_row(self):
        # TODO: not complete
        # create an empty row
        self.new_empty()

        # copy the contents of the above into that
        src_row = self.get_focused_entry()
        src_id = src_row.var_id.get()


    # i and j are lesson_id and they're 1-indexed
    def swap_rows(self, i, j):
        # swaps info of two rows. Works with raw 0 indexed array index values from lesson_entries

        # abort if swapping with itself
        if i == j:
            return
        # make i the smallest, the code below assumes it
        elif i > j:
            i, j = j, i

        # Remember the rows i & j are 1-indexed but the array is 0-indexed

        # Get the relevant information that will be swapped
        entry_i = self.lesson_entries[i - 1]
        topic_i = entry_i.var_topic.get()
        pages_i = entry_i.var_pages.get()
        assignment_i = entry_i.var_assignment.get()
        link_i = entry_i.var_link.get()
        test_i = entry_i.var_test.get()
        cancelled_i = entry_i.var_cancelled.get()
        selected_i = entry_i.var_selected.get()

        entry_j = self.lesson_entries[j - 1]
        topic_j = entry_j.var_topic.get()
        pages_j = entry_j.var_pages.get()
        assignment_j = entry_j.var_assignment.get()
        link_j = entry_j.var_link.get()
        test_j = entry_j.var_test.get()
        cancelled_j = entry_j.var_cancelled.get()
        selected_j = entry_j.var_selected.get()

        # Do the swap

        # swap their colors
        color_i = entry_i.entry_topic["background"]
        color_j = entry_j.entry_topic["background"]
        entry_i.color_row(color_j)
        entry_j.color_row(color_i)

        # swap their info
        entry_i.var_topic.set(topic_j)
        entry_i.var_pages.set(pages_j)
        entry_i.var_assignment.set(assignment_j)
        entry_i.var_link.set(link_j)
        entry_i.var_test.set(test_j)
        entry_i.var_cancelled.set(cancelled_j)
        entry_i.var_selected.set(selected_j)

        entry_j.var_topic.set(topic_i)
        entry_j.var_pages.set(pages_i)
        entry_j.var_assignment.set(assignment_i)
        entry_j.var_link.set(link_i)
        entry_j.var_test.set(test_i)
        entry_j.var_cancelled.set(cancelled_i)
        entry_j.var_selected.set(selected_i)

        # if one of the lessons are marked as odd, also swap their day, week
        # and their colors
        if entry_i.move_all or entry_j.move_all:
            # retrieve the info
            move_all_i = entry_i.move_all
            move_all_j = entry_j.move_all

            day_color_i = entry_i.label_day["fg"]
            day_color_j = entry_j.label_day["fg"]

            day_text_i = entry_i.var_day.get()
            day_text_j = entry_j.var_day.get()

            org_day_i = entry_i.original_day
            org_day_j = entry_j.original_day

            week_text_i = entry_i.var_week.get()
            week_text_j = entry_j.var_week.get()

            duration_i = entry_i.var_duration.get()
            duration_j = entry_j.var_duration.get()

            odd_i = entry_i.odd
            odd_j = entry_j.odd
            

            # swap it

            entry_i.move_all = move_all_j
            entry_j.move_all = move_all_i

            entry_i.label_day.config(fg=day_color_j)
            entry_j.label_day.config(fg=day_color_i)

            entry_i.var_day.set(day_text_j)
            entry_j.var_day.set(day_text_i)

            entry_i.original_day = org_day_j
            entry_j.original_day = org_day_i

            entry_i.var_week.set(week_text_j)
            entry_j.var_week.set(week_text_i)

            entry_i.var_duration.set(duration_j)
            entry_j.var_duration.set(duration_i)

            entry_i.odd = odd_j
            entry_j.odd = odd_i

        # if the lesson is a test or cancelled, swap the time also
        elif (entry_i.var_test.get() or entry_i.var_cancelled.get() or entry_j.var_cancelled.get()\
                or entry_j.var_test.get()):
            duration_i = entry_i.var_duration.get()
            duration_j = entry_j.var_duration.get()

            entry_i.var_duration.set(duration_j)
            entry_j.var_duration.set(duration_i)


    def update_wintitle(self):
        # change the title for the MainWin
        self.title(self.gen_wintitle(self.fpath))


    def gen_wintitle(self, fname) -> str:
        wintitle = "Namnlöst dokument"
        if fname:
            if "/" in fname:
                wintitle = fname.split("/")[-1]  # exclude the path
            elif "\"" in fname:
                wintitle = fname.split("\"")[-1]  # exclude the path
            elif fname:
                wintitle = fname

        return wintitle

    # TODO: when course name is two words, the saved or loaded title gets wrangled. Something with word count
    # and the use of the word med...
    def save_csv(self, saveas=False):
        path = tkinter.filedialog.asksaveasfilename(filetypes=[("Comma-separated values file", "*.csv")])\
        if (saveas or not self.fpath) else self.fpath

        if path is not None and path != "":
            # print("save_csv(): saving to", path)

            # add .csv file ending if its not there
            if path[-4:] != ".csv":# and path is str:
                path += ".csv"

            # update Lesson model object in every entry
            for entry in self.lesson_entries:
                entry.update_model()
            # transfer them to all_lessons[] in Subject model object
            self.subject.all_lessons.clear()
            for entry in self.lesson_entries:
                self.subject.all_lessons.append(entry.lesson)

            # save the headings and info
            s_heading_list = self.var_heading.get().split("med")
            self.subject.name = s_heading_list[0].strip()
            self.subject.group = s_heading_list[1].strip()
            s_info_list = self.var_info.get().split(",")
            self.subject.school = s_info_list[0].strip()
            self.subject.teacher = s_info_list[1].strip()

            # start the thread that counts time since last save
            self.seconds_since_save = 0
            if not self.sec_thread.is_alive():
                try:
                    self.sec_thread.start()
                except RuntimeError:
                    # thread might be already running which causes a runtime error.
                    # for some reason this is not caught by checking threads is_alive()
                    pass

            # thread that changes the save icon to a checkmark when save is complete
            fl_thr = threading.Thread(target=self.flash_button, args=(self.save_button, "limegreen"))
            # write it to disk
            MainWin.write_csv(path, self.subject)
            fl_thr.start()

            self.fpath = path
            self.update_wintitle()
            self.focus_set()

    def flash_button(self, button: Button, color: str):
    # threading func
    # button: the button to flash. color: the color of the flashing
        #print("Thread1: coloring button", color)
        if self.destroyed:
            return

        button.config(image=self.check_image)
        button.image = self.check_image
        #button.update()
        time.sleep(1.5)
        #print("Thread1: coloring button", BUTTON_COLOR)

        if self.destroyed:
            return

        button.config(image=self.save_image)
        button.image = self.save_image

    def count_since_save(self):
    # threading func
    # ticks the time in self that notes seconds since last save
        while self.seconds_since_save < Constants.DONOTASK_SAVE_TIME:
            time.sleep(1.0)
            self.seconds_since_save += 1

    @staticmethod
    def write_csv(file_name, subject):
        with open(file_name, "w", newline="", encoding="utf-8") as subject_file:
            lesson_writer = csv.writer(subject_file, dialect="excel", delimiter=";")
            # Kurs och kursgrupp, kursansvarig och skola
            lesson_writer.writerow([subject.name, subject.group, subject.teacher, subject.school])
            # Rubriker
            lesson_writer.writerow(["Vecka", "Dag", "#", "Innehåll", "Sidor", "Övrigt", "Länk", "Prov", "Inställd",
                                    "Udda", "min"])
            for lesson in subject.all_lessons:
                lesson_writer.writerow([str(lesson.week) + lesson.week_ab, lesson.day, lesson.id, lesson.topic,
                                        lesson.pages, lesson.assignment, lesson.link, lesson.is_test,
                                        lesson.is_cancelled, lesson.is_odd, lesson.duration_min])

    # csv format:
    #
    #
    # row | col-->         0           1       2         3       4        5         6       7         8      9     10
    #  0 (INFO)        subject name  class   teacher   school    -        -         -       -         -      -      -
    #  1 (HEADERS)        week       day      ID      topic   pages  assignment   url     test  cancelled   odd    time
    #  2 and forth (data) str        str      str      str     str      str       str     bool    bool      bool   int

    # opens a csv and displays it
    @staticmethod
    def open_csv(infowin=None):
        file_name = tkinter.filedialog.askopenfilename(filetypes=[("Comma-separated values file", "*.csv")])

        if file_name:
            loaded_sub = MainWin.load_csv(file_name, errormsg=True)

            loaded_win = MainWin(loaded_sub, parent=infowin, fpath=file_name)
            loaded_win.fill_lesson_days()
            loaded_win.fill_org_duration()


            # no, do this directly in the info win instead.
            # hide the InfoWin (=caller)
            # if caller:
            #     if not caller.destroyed:
            #         caller.withdraw()
            loaded_win.mainloop()

        elif infowin is not None:
            # if the user cancels the dialog show the caller again
            infowin.deiconify()

    def prob_org_duration(self, lesson: LessonEntry) -> int:
        target_day = lesson.var_day.get()
        target_week_type = lesson.aorb()
        target_week = lesson.var_week.get()

        for candidate in self.lesson_entries:
            c_day = candidate.var_day.get()
            c_wktp = candidate.aorb()
            c_week = candidate.var_week.get()
            if target_day == c_day and target_week_type == c_wktp and target_week != c_week:
                return candidate.original_duration

        return 0

    def fill_org_duration(self):
        # attempts to fill original durations on tests and cancelled lessons by searching week, week type and day
        # of similar lesson
        for entry in self.lesson_entries:
            if entry.var_test.get() or entry.var_cancelled.get():
                # print("Adjusting org time of:", entry)
                entry.original_duration = self.prob_org_duration(entry)

    def fill_lesson_days(self):
        # if a subject loads from csv, recreate the lesson_days(A/B) arrays in the Subject object
        # fill it up and set() it. These are the days
        if self.lesson_entries[0].aorb():
            la = []
            lb = []

            for entry in self.lesson_entries:
                if (entry.aorb() == "A") and (not entry.odd) and entry.var_day.get() not in la:
                    la.append(entry.var_day.get())
                elif (entry.aorb() == "B") and (not entry.odd) and entry.var_day.get() not in lb:
                    lb.append(entry.var_day.get())

            self.subject.lesson_days_a = la
            self.subject.lesson_days_b = lb
            # print("Lesson days A:", self.subject.lesson_days_a)
            # print("Lesson days B", self.subject.lesson_days_b)

        else:
            ld = []
            for entry in self.lesson_entries:
                if not entry.odd and (not entry.var_day.get() in ld):
                    ld.append(entry.var_day.get())

            self.subject.lesson_days = ld
            # print("fill_lesson_days: Lesson days are:", ld)

    # loads a csv from path file_name and returns a Subject
    @staticmethod
    def load_csv(file_name, caller=None, errormsg=False) -> Subject:
        if not file_name:
            return None

        rows = []
        lessons = []

        # sniff for delimiter (either ; or ,)
        with open(file_name, newline="", encoding="utf-8") as saved_plan:
            if ";" in saved_plan.readline():
                dlm = ";"
            else:
                dlm = ","

            # "rewind" the file
            saved_plan.seek(0, 0)

            # Read all the rows in the csv
            lesson_reader = csv.reader(saved_plan, dialect="excel", delimiter=dlm)
            for row in lesson_reader:
                if row:
                    rows.append(row)

        # saves the faulty row numbers
        err_col_row = []
        err_pars_row = []

        # keeps track of the row nr (1-indexed)
        counter = 1
        # scan rows for errors
        for row in rows:
            # print("Inspecting row", counter, ":", row)
            # check if first row has correct length

            if (counter == 1) and (len(row) < 4):
                # note row that failed
                err_col_row.append(str(counter))
                # print("Error on row: 1 (subject info). " + "len(row) =", len(row))
                # print("Setting default values on strings")
                rows[counter - 1] = ["Kurs", "Klass", "Lärare", "Skola"]

            # check the rest of the rows for correct length
            elif (counter > 2) and (len(row) < 11):
                # note row that failed
                err_col_row.append(str(counter))
                # print("Error on row: " + str(counter) + ", len(row) =", len(row))
                # print("Setting default values on ints and bools")
                # set default values if parsing failed
                rows[counter - 1] = ["1", "mån", counter, row[3], row[4], row[5], row[6], "False", "False", "False",
                                     "60"]

            # when the rows are of correct length, check type correctness
            elif counter > 2:
                # try type conversion on row 3 and forth
                try:
                    # print("Attempting type conversion of non-string data on row", counter, "...")
                    int(row[0][0])
                    # print("Col 1 (week) done")
                    BooleanVar(value=row[7])
                    # print("Col 8 (test) done")
                    BooleanVar(value=row[8])
                    # print("Col 9 (cancelled) done")
                    BooleanVar(value=row[9])
                    # print("Col 10 (odd) done")
                    int(row[10])
                    # print("Col 11 (duration) done")
                except:
                    # note row that failed
                    err_pars_row.append(counter)

                    # print("Type conversion error on row", counter, ": setting default values instead")
                    # set default values if parsing failed
                    rows[counter - 1] = ["1", "mån", counter, row[3], row[4], row[5], row[6], "False", "False", "False",
                                         "60"]

            counter += 1

        if err_col_row and errormsg:
            tkinter.messagebox.showerror(master=caller, title="Inläsningsfel", message="Fel i csv-filen upptäckt.\
            \nFöljande rader hade inte förväntat antal kolumner: " + ", ".join(
                err_col_row) + "\nDe får standardvärden.")

        if err_pars_row and errormsg:
            tkinter.messagebox.showerror(master=caller, title="Inläsningsfel",
                                         message="Fel i csv-filen.\nFöljande rader hade inte förväntad datatyp: "
                                                 + ", ".join(map(str, err_pars_row)) + "\nDe får standardvärden.")

        # save the info from the first row
        subnm, classnm, teachernm, schoolnm = rows[0][0], rows[0][1], rows[0][2], rows[0][3]

        # Trim the first info row and the second heading row
        rows = rows[2:]

        # Create the lessons
        cid = 1
        for row in rows:
            lessons.append(Lesson(week=int(row[0].strip("A").strip("B")),
                                  day=row[1],
                                  id=cid,
                                  topic=row[3],
                                  pages=row[4],
                                  assignment=row[5],
                                  link=row[6],
                                  is_test=True if row[7].lower() == "true" else False,
                                  is_cancelled=True if row[8].lower() == "true" else False,
                                  is_odd=True if row[9].lower() == "true" else False,
                                  duration_min=row[10],
                                  week_ab=row[0][-1] if row[0][-1].isalpha() else "",
                                  ))
            cid += 1

        # create and return the Subject model and give it the properties from the read file
        return Subject(name=subnm, group=classnm, teacher=teachernm, school=schoolnm, all_lessons=lessons)

    # Fills self with lesson info from a csv
    def import_csv(self):
        # ask user to open a file
        file_name = tkinter.filedialog.askopenfilename(filetypes=[("Comma-separated values file", "*.csv")])
        loaded_sub = None
        if file_name is not None and file_name != "":
            # Load the csv to a Subject
            loaded_sub = MainWin.load_csv(file_name, errormsg=False)
        else:
            return

        # find the number of lessons thats cancelled or test, count them to exclude later
        # also uncheck locked lessons so they are included.
        excluded = 0
        for lesson in loaded_sub.all_lessons:
            # uncheck locked lessons to include them
            # has to be done first
            if lesson.is_cancelled and lesson.is_test:
                lesson.is_cancelled = False
                lesson.is_test = False
            # count lessons that are either cancelled or test
            elif lesson.is_cancelled or lesson.is_test:
                excluded += 1

        # find the number of lessons the user has marked as cancelled or test
        ignore = 0
        for entry in self.lesson_entries:
            if entry.var_test.get() or entry.var_cancelled.get():
                ignore += 1

        # create more weeks if the imported csv contains more lessons than lesson_entries currently does
        while len(self.lesson_entries) - ignore < len(loaded_sub.all_lessons) - excluded:
            # print("import_csv(): creating a week to fit import")
            self.create_new_week()

        # fill self with topic, pages and subject
        imp_i = 0  # index for the imported Subject
        emp_i = 0  # index for the empty LessonEntries
        lesson_count = len(loaded_sub.all_lessons)
        while imp_i < lesson_count:
            # dont import entrys that are tests or cancelled
            if (not loaded_sub.all_lessons[imp_i].is_test) and (not loaded_sub.all_lessons[imp_i].is_cancelled):
                if self.lesson_entries[emp_i].var_test.get() or self.lesson_entries[emp_i].var_cancelled.get():
                    emp_i += 1  # increment the array without importing
                    continue
                else:
                    self.lesson_entries[emp_i].var_topic.set(loaded_sub.all_lessons[imp_i].topic)
                    self.lesson_entries[emp_i].var_pages.set(loaded_sub.all_lessons[imp_i].pages)
                    self.lesson_entries[emp_i].var_assignment.set(loaded_sub.all_lessons[imp_i].assignment)
                    self.lesson_entries[emp_i].odd = loaded_sub.all_lessons[imp_i].is_odd
                    self.lesson_entries[emp_i].var_link.set(loaded_sub.all_lessons[imp_i].link)
                    emp_i += 1  # increment the empty array since a position was succesfully filled

            imp_i += 1

        self.fill_lesson_days()


if __name__ == "__main__":
    root = Tk()
    root.destroyed = True
    root.withdraw()
    MainWin.open_csv(root)
