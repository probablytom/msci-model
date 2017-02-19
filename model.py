from resp_classes import Student, Lecturer, Constraint, Responsibility
from resp_classes import Obligation
from theatre_ag import SynchronizingClock

global_clock = SynchronizingClock()

# Create a bunch of lecturers and students.

students = []
for i in range(5):
    students.append(Student([], "student_"+str(i), global_clock))

lecturers = []
for i in range(3):
    lecturers.append(Lecturer([], "lecturer_"+str(i), global_clock))

# TODO: What's the best way to encode the constraint text?
first_essay_deadline = Constraint('time', 'ticks = 10')
second_essay_deadline = Constraint('time', 'ticks = 20')
write_essay_constraint = Constraint('writing', 'essays_written += 1')
write_code_constraint = Constraint('development', 'working_programs += 1')

# Extracurricular activity constraints:
research_writing_duration = Constraint('time', 'ticks = 15')
research_writing_activity = Constraint('writing', 'essays_written += 1')
research_programming_duration = Constraint('time', 'ticks = 15')
research_programming_activity = Constraint('development', 'working_programs += 1')
