# encoding: utf-8
from Constants import *


class Lesson:

    def __init__(self, week: int, day, id=0, week_ab="", topic="", location="", duration_min=60, pages="", link="",
                 assignment="", is_test=False, is_cancelled=False, is_odd=False):

        self.id = id
        self.week = week
        self.day = day
        self.week_ab = week_ab
        self.topic = topic
        self.location = location
        self.duration_min = duration_min
        self.pages = pages
        self.assignment = assignment
        self.link = link
        self.is_test = is_test
        self.is_cancelled = is_cancelled
        self.is_odd = is_odd

    @staticmethod
    def get_invalid_days(days=None) -> tuple:
        if not days:
            days = ()

        inv_days = []
        ok_days = DAY_COMP.keys()
        # find the ones that aren't
        for day in days:
            if day not in ok_days:
                inv_days.append(day)
        del days
        return tuple(inv_days)

    def __str__(self) -> str:
        return "Lesson #" + str(self.id) + ", W: " + str(self.week) + self.week_ab + " " + self.day

