# encoding: utf-8

# Keeps track of the subject as a whole

from Lesson import Lesson


class Subject:

    def __init__(self, name="Kursnamn", group="Kursgrupp", teacher="Lärare", school="Skola", start_week=34,
                 end_week=2, week_breaks=None, lesson_days=None, lesson_days_a=None, lesson_days_b=None,
                 all_lessons=None):

        if not week_breaks:
            week_breaks = []

        if not lesson_days:
            lesson_days = []

        if not lesson_days_a:
            lesson_days_a = []

        if not lesson_days_b:
            lesson_days_b = []

        if not all_lessons:
            all_lessons = []

        self.name = name
        self.group = group
        self.teacher = teacher
        self.school = school
        self.start_week = start_week
        self.end_week = end_week
        self.week_breaks = list(week_breaks)
        self.lesson_days = lesson_days
        self.lesson_days_a = lesson_days_a
        self.lesson_days_b = lesson_days_b
        self.all_lessons = all_lessons

    def create_lessons_ab(self):
        # Generate a list of the weeks of the specified period
        weeks = []
        if self.end_week < self.start_week:  # Then we have a course that spans over christmas
            fall = range(self.start_week, 52)
            spring = range(2, self.end_week+1)
            weeks = list(fall) + list(spring)
        else:
            weeks = list(range(self.start_week, self.end_week+1))

        # create the lessons from the template, beginning with id=1 and A-week
        # print("self.week_breaks =", self.week_breaks)
        lesson_id = 1
        a_week = True
        for week in weeks:
            if week in self.week_breaks:
                # print("Week", week, "is a break")
                continue
            elif a_week:
                for day in self.lesson_days_a:
                    new_lesson = Lesson(week, day, week_ab="A")
                    new_lesson.id = lesson_id
                    lesson_id += 1
                    self.all_lessons.append(new_lesson)
            else:
                for day in self.lesson_days_b:
                    new_lesson = Lesson(week, day, week_ab="B")
                    new_lesson.id = lesson_id
                    lesson_id += 1
                    self.all_lessons.append(new_lesson)
            a_week = not a_week

    def create_lessons(self):
        # Generate a list of the weeks of the specified period
        weeks = []
        # print("Subject.create_lessons(): start =", self.start_week, "end =", self.end_week)
        if self.end_week < self.start_week:  # Then we have a course that spans over christmas
            fall = range(self.start_week, 52)
            spring = range(2, self.end_week+1)
            weeks = list(fall) + list(spring)
        else:
            weeks = list(range(self.start_week, self.end_week+1))

        lesson_id = 1
        for week in weeks:
            for day in self.lesson_days:
                new_lesson = Lesson(week, day)
                new_lesson.id = lesson_id
                lesson_id += 1
                self.all_lessons.append(new_lesson)

    def get_lessons(self, week: int) -> tuple:
        le_w = []

        for le in self.all_lessons:
            if le.week == week:
                le_w.append(le)

        return tuple(le_w)

    def num_lessons(self, week: int) -> int:
        return len(self.get_lessons(week))


    def week_aorb(self, week: int) -> str:
        lessons = self.get_lessons(week)
        return lessons[0].week_ab


if __name__ == "__main__":
    s = Subject("Kemi 1", "NA20c", start_week=34, end_week=20, lesson_days_a=["mån","tis"], lesson_days_b=["ons", "tors"])
    s.create_lessons_ab()
    for lesson in s.all_lessons:
        print(lesson)
