# encoding: utf-8
# exports a Subject to an xlsx file.

from xlsxwriter import *
from Subject import Subject
from Lesson import Lesson
import Constants


def export_subject(s: Subject, xpath: str = ""):
    wb = Workbook(xpath + "/" + s.name + " " + s.group + " " + s.teacher + ".xlsx")
    ws = wb.add_worksheet()

    ##############################
    #      STYLES FOR CELLS      #
    ##############################

    info_f = wb.add_format({"italic":True, "font_size":9})

    title_f = wb.add_format({"bold":True, "font_size":14})
    title_f.set_align("top")

    heading_f = wb.add_format({"bold":True, "font_size":12})
    heading_f.set_top(1) #5 för tjockare
    heading_f.set_bottom(1)
    heading_f.set_left(1)
    heading_f.set_right(1)
    heading_f.set_align("vcenter")
    heading_f.set_align("center")

    heading_top_f = wb.add_format({"bold":True, "font_size":12})
    heading_top_f.set_top(1) #5 för tjockare
    heading_top_f.set_left(1)
    heading_top_f.set_right(1)
    heading_top_f.set_align("vcenter")

    heading_middle_f = wb.add_format({"bold":True, "font_size":12})
    heading_middle_f.set_left(1)
    heading_middle_f.set_right(1)

    heading_bottom_f = wb.add_format({"bold":True, "font_size":12})
    heading_bottom_f.set_bottom(1)
    heading_bottom_f.set_left(1)
    heading_bottom_f.set_right(1)

    # styles for top, middle and bottom
    single_row_f = wb.add_format({"font_size": 10})
    single_row_f.set_top(1)
    single_row_f.set_bottom(1)
    single_row_f.set_text_wrap()

    top_row_f = wb.add_format({"font_size": 10})
    top_row_f.set_top(1)
    top_row_f.set_left(1)
    top_row_f.set_right(1)
    top_row_f.set_text_wrap()
    top_row_f.set_align("top")
    top_row_f.set_align("vjustify")

    middle_row_f = wb.add_format({"font_size": 10})
    middle_row_f.set_left(1)
    middle_row_f.set_right(1)
    middle_row_f.set_text_wrap()
    middle_row_f.set_align("top")

    bottom_row_f = wb.add_format({"font_size": 10})
    bottom_row_f.set_bottom(1)
    bottom_row_f.set_left(1)
    bottom_row_f.set_right(1)
    bottom_row_f.set_text_wrap()
    bottom_row_f.set_align("center")
    bottom_row_f.set_align("vcenter")

    # colors for test and cancelled
    test_color = "#eee685"
    cancelled_color = "#eee9e9"
    link_color = "#0000EE"

    top_cancelled = copy_format(wb, top_row_f)
    top_cancelled.set_bg_color(cancelled_color)
    middle_cancelled = copy_format(wb, middle_row_f)
    middle_cancelled.set_bg_color(cancelled_color)
    bottom_cancelled = copy_format(wb, bottom_row_f)
    bottom_cancelled.set_bg_color(cancelled_color)

    top_test = copy_format(wb, top_row_f)
    top_test.set_bg_color(test_color)
    middle_test = copy_format(wb, middle_row_f)
    middle_test.set_bg_color(test_color)
    bottom_test = copy_format(wb, bottom_row_f)
    bottom_test.set_bg_color(test_color)

    formats = ((top_row_f, middle_row_f, bottom_row_f),
               (top_cancelled, middle_cancelled, bottom_cancelled),
               (top_test, middle_test, bottom_test))

    #   WRITE DAY ROW AND WEEK COLUMN    #
    days = sort_days(tuple(set([lesson.day for lesson in s.all_lessons])))

    # creates a tuple of sorted weeks as ints (to enable sorting)
    weeks = sorted(list((set([int(lesson.week) for lesson in s.all_lessons]))))

    # put A or B into the week numbers
    weeks_str = []
    for week in weeks:
        weeks_str.append(str(week)+s.week_aorb(week))

    # put ht-weeks before vt-weeks.
    weeks_ht = []
    weeks_vt = []
    for week in weeks_str:
        test_week = week[0:-1] if not week[-1].isdecimal() else week
        if int(test_week)>=32 and int(test_week)<=52:
            weeks_ht.append(week)
        else:
            weeks_vt.append(week)

    weeks = weeks_ht + weeks_vt
    # print('weeks_str is', weeks_str)
    # print("ht+vt is", weeks)
    row = 1
    col = 1
    ws.set_row(0, height=30)
    ws.write(row, col-1, "Vecka", heading_f)

    # write day headings
    # ws.set_row(row, height=30)
    ws.set_column(col, col+len(days)-1, width=20)
    for day in days:
        ws.write(row, col, day, heading_f)
        col += 1


    # write a column of weeks
    row = 2
    col = 0
    for week in weeks_str:
        # print('Printing week number ', week)
        ws.write(row, col, week, heading_top_f)
        ws.set_row(row, height=25)
        ws.write(row+1, col, "", heading_middle_f)
        ws.write(row+2, col, "", heading_bottom_f)
        row += 3

    #       WRITE LESSONS TO CELLS       #
    row = 2
    col = 1

    for row_counter in range(len(weeks)):
        week = weeks[row_counter]
        for col_counter in range(len(days)):
            day = days[col_counter]
            write_lesson(s, row+3*row_counter, col+col_counter, week, day, wb, ws, formats)

    # header
    ws.set_header(s.school+" / "+s.teacher)

    # title
    ws.merge_range("A1:C1", "Planering " + s.name + " " + s.group, title_f)

    wb.close()

def write_lesson(subject, row, col, week, day, wb, ws, formats: tuple):

    # search subject for the lesson matching week and day. If not found, mark as cancelled.
    lesson_found = False
    for lesson in subject.all_lessons:
        w_str = str(lesson.week) + lesson.week_ab
        if lesson.day == day and w_str == week:
            lesson_found = True

            # determine correct format:
            tf = None
            mf = None
            bf = None
            if lesson.is_test and not lesson.is_cancelled: # lesson is test
                tf = formats[2][0]
                mf = formats[2][1]
                bf = formats[2][2]
            elif not lesson.is_test and lesson.is_cancelled: # lesson is cancelled
                tf = formats[1][0]
                mf = formats[1][1]
                bf = formats[1][2]
            else: # ordinary lesson (include locked lessons)
                tf = formats[0][0]
                mf = formats[0][1]
                bf = formats[0][2]

            ws.write(row, col, lesson.topic, tf)
            if lesson.pages:
                ws.write(row+1, col, "s. " + lesson.pages if lesson.pages[0] != "s" else "" + lesson.pages, mf)
            else:
                ws.write(row+1, col, lesson.pages, mf)

            if lesson.link:
                bf.set_font_color("#0000EE")
                bf.set_underline()
                ws.write_url(row+2, col, string="Länk", url=lesson.link, cell_format=bf)
                bf.set_font_color("#000000")
            else:
                ws.write(row+2, col, "", bf)

    if not lesson_found:
        ws.write(row, col, "", formats[1][0])
        ws.write(row + 1, col, "", formats[1][1])
        ws.write(row + 2, col, "", formats[1][2])

def sort_days(days: tuple) -> tuple:
    # create a list of blanks
    sorted_days = ["" for _ in range(7)]

    # put the days in, in correct order
    for day in days:
        if day not in sorted_days:
            sorted_days[Constants.DAY_COMP.get(day)] = day

    # don't return the dummy days
    rl = []
    for day in sorted_days:
        if day:
            rl.append(day)
    return tuple(rl)

def copy_format(book, fmt):
    properties = [f[4:] for f in dir(fmt) if f[0:4] == 'set_']
    dft_fmt = book.add_format()
    return book.add_format({k : v for k, v in fmt.__dict__.items() if k in properties and dft_fmt.__dict__[k] != v})