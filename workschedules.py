import copy
# https://freecontent.manning.com/constraint-satisfaction-problems-in-python/
# https://www.reddit.com/r/compsci/comments/1g72fd/work_scheduling_algorithm/
# http://aima.cs.berkeley.edu/newchap05.pdf


class Student:
    def __init__(self, name, busy: {}, hours: int, jobs: list):
        self.name = name
        self.busy = busy
        self.hours = hours
        self.jobs = jobs

        for j in self.jobs:
            j.addStudent(self)
        all_students.append(self)

    def is_free(self, hour, day):
        return hour not in self.busy[day]

    def timeUntilClass(self, day, hour, close):
        busy = self.busy[day]

        if not busy or max(busy) <= hour:
            return close - hour

        time = 0
        for t in busy:
            # is before a class
            if t > close:
                return close - hour
            if hour < t:
                time = t - hour
                break
        return time

    def timePrevClass(self, day, hour, open_time):
        busy = self.busy[day]

        # no classes before
        if not busy or min(busy) >= hour:
            return hour - open_time

        time = 0
        for t in busy:
            # is after a class
            if hour > t:
                time = hour - t
            else:
                break
        return time

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Shift:
    def __init__(self, name, time_range):
        self.name = name
        self.timeRange = time_range
        self.students = []
        self.students_available = {"Monday": {}, "Tuesday": {}, "Wednesday": {}, "Thursday": {}, "Friday": {},
                                   "Saturday": {}, "Sunday": {}}
        self.student_working = {"Monday": {}, "Tuesday": {}, "Wednesday": {}, "Thursday": {}, "Friday": {},
                                "Saturday": {}, "Sunday": {}}

        # self.counter = 0
        # self.possible_results = []

        for day in self.students_available:
            if self.timeRange[day] != "Closed":
                t_open, t_close = self.timeRange[day]
                for hour in range(t_open, t_close):
                    self.students_available[day][hour + 0.0] = []
                    self.students_available[day][hour + .5] = []

        for day in self.student_working:
            if self.timeRange[day] != "Closed":
                t_open, t_close = self.timeRange[day]
                for hour in range(t_open, t_close):
                    self.student_working[day][hour + 0.0] = ""
                    self.student_working[day][hour + .5] = ""

    def addStudent(self, student):
        # sanity check
        if self not in student.jobs:
            print("not included in job")
            return

        self.students.append(student)
        for day in self.students_available:
            if self.timeRange[day] != "Closed":
                for time in self.students_available[day]:
                    if student.is_free(time, day):
                        self.students_available[day][time].append(student)

    def __str__(self):
        return self.name + str(id(self))

    def __repr__(self):
        return self.name + str(id(self))


def succ():
    return 1


def isGoal(assignment):
    for p in assignment:
        for day in assignment[p]:
            for time in assignment[p][day]:
                if assignment[p][day][time] == "":
                    return False
    return True


def get_hours(assignment, worker):
    count = 0
    for parent in assignment:
        for day in assignment[parent]:
            for time in assignment[parent][day]:
                if assignment[parent][day][time] and assignment[parent][day][time].name == worker.name:
                    count += 0.5

    return count


def consistent(assignment, parent, worker, time, day):
    working_elsewhere = False
    for p in assignment:
        if p.name == parent.name:
            continue

        if time in assignment[p][day]:
            if assignment[p][day][time] and assignment[p][day][time].name == worker.name:
                working_elsewhere = True

            # if time == 12.5 and day == "Monday":
            #     print(worker, assignment[p][day][time], parent, " = ", working_elsewhere)

    return worker.is_free(time, day) and get_hours(assignment, worker) < worker.hours and not working_elsewhere


def timeWorkedToday(assignment, student, day):
    count = 0
    for parent in assignment:
        for t in assignment[parent][day]:
            if assignment[parent][day][t] and assignment[parent][day][t].name == student.name:
                count += 1
    return count / 2


def score_and_sort(parent, assignment, day, time):
    score = []
    available = parent.students_available[day][time]
    shift_length = 4.5

    testing = False
    if parent.name == "SS" and (time == 16.0) and day == "Tuesday":
        testing = True
    for student in available:
        if consistent(assignment, parent, student, time, day):
            t_open, t_close = parent.timeRange[day]

            next_class = student.timeUntilClass(day, time, t_close)
            prev_class = student.timePrevClass(day, time, t_open)
            worked = timeWorkedToday(assignment, student, day)

            s = 5

            r = [x * 0.5 for x in range(t_open * 2, t_close * 2)]
            for t in r:
                if assignment[parent][day][t] and assignment[parent][day][t].name == student.name:
                    if (t >= max(time-shift_length, time-prev_class)) and (t <= min(time+shift_length, time+next_class)):
                        s+=10
                    else:
                        s-=100

                    if t >= t_close - 3:
                        s += 15
            s *=  min(shift_length, next_class + prev_class) / shift_length

            # if student.name == "Amy (6)" and parent.name == "THD" and day == "Friday":
            #     print(max(time - shift_length, time - prev_class), min(time + shift_length, time + next_class))
            #     print(time, s)
            #r = [x * 0.5 for x in range(int(time-prev_class) * 2, int(time+next_class-0.5) * 2)]
            #for t in r:
                #if assignment[parent][day][t] and assignment[parent][day][t].name == student.name:
                    #s += 20

            # neighboring shifts aren't assigned
            # if (time != t_open and assignment[parent][day][time-0.5] == "") \
            #         or (time < t_close-0.5 and assignment[parent][day][time+0.5] == ""):
            #     s += 10*min(shift_length, next_class + prev_class)/shift_length


            # # work the shift before/after
            # if (time != t_open and assignment[parent][day][time-0.5] == student) \
            #         or (time < t_close-0.5 and assignment[parent][day][time+0.5] == student):
            #     s += 15
            #     if time >= t_close - 3:
            #         s += 15
            #
            #     if (time != t_open and not assignment[parent][day][time - 0.5] == student) \
            #             or (time < t_close - 0.5 and not assignment[parent][day][time + 0.5] == student):
            #         if worked > shift_length and time < t_close - 3:
            #             s -= 4*worked
            # else:
            #     # worked another section of day
            #     if worked > 0:
            #         s -= 30
            #     days_worked = 0
            #     days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            #     for d in days:
            #         if timeWorkedToday(assignment, student, d) > 0:
            #             days_worked += 1
            #     s *= (min(student.hours, student.hours - days_worked*shift_length)) / student.hours

            if s < 0:
                s = 1/s

            # greater hrs, greater score
            score.append((student, s))

    score.sort(key=lambda x: x[1], reverse=True)

    if testing:
        print(score)

    returnVal = [student for student, s in score]
    return returnVal


def bt(assignment):
    unassigned = []
    for p in assignment:
        shifts = assignment[p]
        for day in shifts:
            for time in shifts[day]:
                if shifts[day][time] == "":
                    unassigned.append((p, day, time))
    # check if goal
    if not unassigned:
        global possible_results
        global counter
        global result_amt
        counter += 1
        if assignment not in possible_results:
            temp = copy.deepcopy(assignment)
            # temp = assignment.copy()
            possible_results.append(temp)
        if len(possible_results) >= result_amt:
            return assignment
        return None

    # sort by mvp
    # unassigned.sort(key=lambda a: len(a[0].students_available[a[1]][a[2]]))
    if unassigned:
        parent0, day0, time0 = unassigned.pop(0)
        rated_studentAvail = score_and_sort(parent0, assignment, day0, time0)
        for worker in rated_studentAvail:
            local_assignment = assignment.copy()
            # local_assignment = copy.deepcopy(assignment)
            # p = [i for i in local_assignment.keys() if i.name == parent.name][0]
            # print(p)
            local_assignment[parent0][day0][time0] = worker

            result = bt(local_assignment)
            if result:
                return result

    return None


def test(assignment):
    print()

    for s in all_students:
        hours = get_hours(possible_results[k], s)
        if hours > s.hours:
            print(f'\nERROR: {hours-s.hours} extra hours for {s}')
        print(f'{s} is working {hours}')

    print()

    t_open = min([i[0] for parent in assignment.keys() for i in parent.timeRange.values() if type(i) == tuple])
    t_close = max([i[1] for parent in assignment.keys() for i in parent.timeRange.values() if type(i) == tuple])
    r = (x * 0.5 for x in range(t_open * 2, t_close * 2))
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for time in r:
        for day in days:
            workers = []
            for parent in assignment:
                if time in assignment[parent][day]:
                    s = assignment[parent][day][time].name
                    if s in workers:
                        print(f'ERROR: {s} already worked at {time}, {day}, {parent}')
                    else:
                        workers.append(s)


def print_assignment(assignment):
    for parent in assignment:
        print("-" * 20, parent, "-" * 20)
        print(
            "{:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15}".format("    Monday", "Tuesday", "Wednesday", "Thursday",
                                                                      "Friday", "Saturday", "Sunday"))

        result = assignment[parent]
        time_list = [i for i in parent.timeRange.values() if type(i) == tuple]
        t_open, t_close = min([i[0] for i in time_list]), max([i[1] for i in time_list])
        r = (x * 0.5 for x in range(t_open * 2, t_close * 2))
        for i in r:
            res = []
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

            for day in days:
                if parent.timeRange[day] == "Closed":
                    continue

                o, c = parent.timeRange[day]
                if (o <= i) and (c > i):
                    res.append(result[day][i].name)
                else:
                    res.append("    X     ")

            for x in range(7-len(res)):
                res.append("    X     ")

            m, t, w, r, f, s, u = res
            print(i, " {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15}".format(m, t, w, r, f, s, u))
    test(assignment)


possible_results = []
counter = 0
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    data1 = {'Monday': [12.5, 13.0, 13.5, 14.0, 14.5],
             'Tuesday': [10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5],
             'Wednesday': [11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5],
             'Thursday': [10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5],
             'Friday': [12.5, 13, 13.5, 14, 14.5],
             'Saturday': [], 'Sunday': []}
    data2 = {'Monday': [9, 9.5, 10, 10.5],
             'Tuesday': [8, 8.5, 9, 9.5, 11, 11.5, 12, 12.5, 13, 13.5],
             'Wednesday': [9, 9.5, 10, 10.5, 18.5, 19, 19.5, 20, 20.5, 21, 22.5, 23],
             'Thursday': [8, 8.5, 9, 9.5, 11, 11.5, 12, 12.5, 13, 13.5],
             'Friday': [9, 9.5, 10, 10.5, 13, 13.5, 14, 14.5],
             'Saturday': [], 'Sunday': []}
    data3 = {'Monday': [10, 10.5, 11, 12, 12.5, 14, 14.5, 15],
             'Tuesday': [8, 8.5, 9, 9.5, 12, 12.5],
             'Wednesday': [10, 10.5, 11, 12, 12.5, 14, 14.5, 15],
             'Thursday': [8, 8.5, 9, 9.5, 12, 12.5],
             'Friday': [12, 12.5, 13, 13.5],
             'Saturday': [], 'Sunday': []}
    data4 = {'Monday': [12, 12.5, 13, 13.5],
             'Tuesday': [8, 8.5, 9, 9.5, 13, 13.5],
             'Wednesday': [12, 12.5, 13, 13.5, 14, 14.5],
             'Thursday': [8, 8.5, 9, 9.5],
             'Friday': [9, 9.5, 13, 13.5],
             'Saturday': [], 'Sunday': []}
    data5 = {'Monday': [10, 10.5, 12, 12.5, 13, 16, 16.5, 17],
             'Tuesday': [10, 10.5, 16, 16.5, 17],
             'Wednesday': [10, 10.5, 12, 12.5, 13, 16, 16.5, 17],
             'Thursday': [10, 10.5, 16, 16.5, 17],
             'Friday': [10, 10.5, 11, 11.5],
             'Saturday': [], 'Sunday': []}
    data6 = {'Monday': [10, 10.5, 11, 14, 14.5, 15, 15.5],
             'Tuesday': [12, 12.5, 13, 13.5],
             'Wednesday': [10, 10.5, 11, 14, 14.5, 15, 15.5],
             'Thursday': [12, 12.5, 13, 13.5],
             'Friday': [12, 12.5],
             'Saturday': [], 'Sunday': []}
    data7 = {'Monday': [10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5],
             'Tuesday': [10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 16, 16.5],
             'Wednesday': [10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5],
             'Thursday': [10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 16, 16.5],
             'Friday': [11, 11.5],
             'Saturday': [], 'Sunday': []}
    data8 = {'Monday': [8.5, 9, 9.5, 10, 10.5, 11, 12, 12.5, 14, 14.5],
             'Tuesday': [8, 8.5, 14, 14.5],
             'Wednesday': [8.5, 9, 9.5, 10, 10.5, 11, 12, 12.5, 14, 14.5],
             'Thursday': [8, 8.5],
             'Friday': [9, 9.5, 14, 14.5],
             'Saturday': [], 'Sunday': []}

    data9 = {'Monday': [10, 10.5, 11, 15.5, 16, 16.5, 17, 17.5],
             'Tuesday': [14, 14.5, 15],
             'Wednesday': [10, 10.5, 11, 15, 15.5, 16, 16.5, 17, 17.5],
             'Thursday': [10, 10.5, 14, 14.5, 15],
             'Friday': [],
             'Saturday': [], 'Sunday': []}

    data10 = {'Monday': [10, 10.5],
              'Tuesday': [8, 8.5, 9, 9.5, 10, 10.5, 14, 14.5, 15, 15.5],
              'Wednesday': [10, 10.5],
              'Thursday': [8, 8.5, 9, 9.5, 14, 14.5, 15, 15.5],
              'Friday': [8, 8.5, 9, 9.5, 10, 10.5],
              'Saturday': [], 'Sunday': []}

    data11 = {'Monday': [10, 10.5, 11, 11.5, 16, 16.5, 17, 17.5],
              'Tuesday': [12, 12.5, 13],
              'Wednesday': [10, 10.5, 11, 11.5, 16, 16.5, 17, 17.5],
              'Thursday': [], 'Friday': [10, 10.5, 11, 11.5],
              'Saturday': [], 'Sunday': []}

    data12 = {'Monday': [14, 14.5, 15, 16, 16.5, 17],
              'Tuesday': [],
              'Wednesday': [14, 14.5, 15, 16, 16.5, 17],
              'Thursday': [12, 12.5, 13], 'Friday': [15, 15.5, 16, 16.5],
              'Saturday': [], 'Sunday': []}

    # data9 = {'Monday': [8.5, 9, 9.5, 14, 14.5],
             # 'Tuesday': [8, 8.5, 14, 14.5],
             # 'Wednesday': [8.5, 9, 9.5, 14, 14.5],
             # 'Thursday': [8, 8.5], 'Friday': [9, 9.5, 14, 14.5],
             # 'Saturday': [], 'Sunday': []}

    all_students = []
    SS = Shift("SS", {"Monday": (8, 17), "Tuesday": (8, 17), "Wednesday": (8, 17), "Thursday": (8, 17),
                      "Friday": (8, 17), "Saturday": "Closed", "Sunday": "Closed"})
    COE = Shift("COE", {"Monday": (8, 20), "Tuesday": (8, 20), "Wednesday": (8, 20), "Thursday": (8, 20),
                        "Friday": (8, 20), "Saturday": "Closed", "Sunday": "Closed"})
    THD = Shift("THD", {"Monday": (8, 21), "Tuesday": (8, 21), "Wednesday": (8, 21), "Thursday": (8, 21),
                        "Friday": (8, 18), "Saturday": "Closed", "Sunday": "Closed"})

    Person1 = Student("Steve (1)", data1, 25, [SS, COE, THD])
    Person2 = Student("Bob (2)", data2, 25, [SS, COE, THD])
    Person3 = Student("Kat (3)", data3, 25, [SS, COE, THD])
    Person4 = Student("Emily (4)", data4, 25, [SS, COE, THD])
    Person5 = Student("Bill (5)", data5, 25, [SS, COE, THD])
    Person6 = Student("Amy (6)", data6, 25, [SS, COE, THD])
    Person7 = Student("Tiffany (7)", data7, 10, [SS, COE, THD])
    Person8 = Student("Rick (8)", data8, 25, [SS, COE, THD])
    Person9 = Student("Ally (9)", data9, 25, [SS, COE, THD])
    Person10 = Student("Jill (10)", data10, 25, [SS, COE, THD])
    Person11 = Student("Sam (11)", data11, 25, [SS, COE, THD])
    Person12 = Student("Becka (12)", data12, 10, [SS, COE, THD])

    # days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    # assignment = {SS: SS.student_working, COE: COE.student_working}
    a = {SS: SS.student_working, COE: COE.student_working, THD: THD.student_working}
    result_amt = 1

    bt(a)

    # print("len", len(possible_results))
    # print("counter", counter)
    # print(possible_results)
    if possible_results:
        for k in range(0, len(possible_results)):
            if k != 0:
                print("="*100)
            print_assignment(possible_results[k])
