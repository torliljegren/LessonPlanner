# encoding: utf-8

from xlsxwriter import *
from Subject import Subject
from Lesson import Lesson


def export_subject(s: Subject, xpath: str = ""):

    ##############################
    #      STYLES FOR CELLS      #
    ##############################

    wb = Workbook(xpath+"/"+s.name+" "+s.group+" "+s.teacher+".xlsx")
    ws = wb.add_worksheet()

    info_f = wb.add_format({"italic":True, "font_size":9})

    title_f = wb.add_format({"bold":True, "align":"center", "font_size":14})

    heading_f = wb.add_format({"bold":True, "font_size":11})
    heading_f.set_bottom(2) #5 för tjockare

    single_row_f = wb.add_format({"font_size":11})
    single_row_f.set_top(1)
    single_row_f.set_bottom(1)
    single_row_f.set_text_wrap()

    top_row_f = wb.add_format({"font_size":11})
    top_row_f.set_top(1)
    top_row_f.set_bottom(4)
    top_row_f.set_text_wrap()

    middle_row_f = wb.add_format({"font_size":11})
    middle_row_f.set_top(4)
    middle_row_f.set_bottom(4)
    middle_row_f.set_text_wrap()

    bottom_row_f = wb.add_format({"font_size":11})
    bottom_row_f.set_top(4)
    bottom_row_f.set_bottom(1)
    bottom_row_f.set_text_wrap()


    ##############################
    #       WRITE TO CELLS       #
    ##############################

    # set width of cells
    ws.set_column(0,1,5)
    ws.set_column(2,2,3)
    ws.set_column(3,3,35)
    ws.set_column(4,5, 12)

    # info row
    ws.write(0, 0, s.teacher+", "+s.school, info_f)

    # title
    ws.merge_range("A3:F3", s.name+" med "+s.group, title_f)

    # headings
    ws.write(5, 0, "Vecka", heading_f)
    ws.write(5, 1, "Dag", heading_f)
    ws.write(5, 2, "#", heading_f)
    ws.write(5, 3, "Innehåll", heading_f)
    ws.write(5, 4, "Sidor", heading_f)
    ws.write(5, 5, "Övrigt", heading_f)
    ws.write(5, 6, "Video", heading_f)

    row, col = 6, 0

    counter = 0

    for lesson in s.all_lessons:
        # keeps track of how often a week occurs
        freq = s.num_lessons(lesson.week)

        if freq == 1:
            # format single
            write_lesson(lesson, row, col, wb, ws, single_row_f)
        else:
            if counter == 0:
            # format top
                write_lesson(lesson, row, col, wb, ws, top_row_f)
                counter += 1
            elif counter == freq-1:
            # format bottom
                write_lesson(lesson, row, col, wb, ws, bottom_row_f)
                # reset counter
                counter = 0
            else:
            # middle
                write_lesson(lesson, row, col, wb, ws, middle_row_f)
                counter += 1
        row += 1

    wb.close()


def write_lesson(l: Lesson, row: int, col: int, wb, ws, ws_f):
    # ws: Worksheet from xlsxwriter Workbook. ws_f: Format from ws

    ws.set_row(row, 30)

    # adjust the format to match colored bg for test and cancelled
    if l.is_test and not l.is_cancelled:
        f_ye = wb.add_format({"font_size":11})
        f_ye.set_top(ws_f.top)
        f_ye.set_bottom(ws_f.bottom)
        f_ye.set_text_wrap()
        f_ye.set_bg_color("#EEE46B")
        ws.write_number(row, col, int(l.week), ws_f)
        ws.write(row, col + 1, l.day, ws_f)
        ws.write_number(row, col + 2, int(l.id), ws_f)
        ws.write(row, col + 3, l.topic, f_ye)
        ws.write(row, col + 4, l.pages, f_ye)
        ws.write(row, col + 5, l.assignment, f_ye)

        if l.link:
            ws.write_url(row, col + 6, url=l.link, string="Länk",cell_format=f_ye)
        else:
            ws.write(row, col + 6, l.link, f_ye)

    elif l.is_cancelled and not l.is_test:
        f_sv = wb.add_format({"font_size":11})
        f_sv.set_top(ws_f.top)
        f_sv.set_bottom(ws_f.bottom)
        f_sv.set_text_wrap()
        f_sv.set_bg_color("#C3BDBD")
        ws.write_number(row, col, int(l.week), ws_f)
        ws.write(row, col + 1, l.day, ws_f)
        ws.write_number(row, col + 2, int(l.id), ws_f)
        ws.write(row, col + 3, l.topic, f_sv)
        ws.write(row, col + 4, l.pages, f_sv)
        ws.write(row, col + 5, l.assignment, f_sv)

        if l.link:
            ws.write_url(row, col + 6, url=l.link, string="Länk", cell_format=f_sv)
        else:
            ws.write(row, col + 6, l.link, f_sv)

    else:
        ws.write_number(row, col, int(l.week), ws_f)
        ws.write(row, col + 1, l.day, ws_f)
        ws.write_number(row, col + 2, int(l.id), ws_f)
        ws.write(row, col + 3, l.topic, ws_f)
        ws.write(row, col + 4, l.pages, ws_f)
        ws.write(row, col + 5, l.assignment, ws_f)

        if l.link:
            ws.write_url(row, col + 6, url=l.link, string="Länk",cell_format=ws_f)
        else:
            ws.write(row, col + 6, l.link, ws_f)
