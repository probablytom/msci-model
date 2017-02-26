from resp_classes import Student, Lecturer, Constraint, Obligation
from theatre_ag import SynchronizingClock

# TODO: What's the model duration?
global_clock = SynchronizingClock(max_ticks=100)

# Create a bunch of lecturers and students.


# TODO: What notions should a student have to begin with?

students = []
for i in range(5):
    curr_student = Student([], "student_"+str(i), global_clock)
    curr_student.start()
    students.append(curr_student)


# TODO: What notions should a lecturer have to begin with?

lecturers = []
for i in range(3):
    curr_lecturer = Lecturer([], "lecturer_"+str(i), global_clock)
    curr_lecturer.start()
    lecturers.append(curr_lecturer)


# TODO: What's the best way to encode the constraint text?
essay_deadline = Constraint('time', 'ticks = 10')
programming_deadline = Constraint('time', 'ticks = 15')
write_essay_constraint = Constraint('writing', 'essays_written += 1')
write_code_constraint = Constraint('development', 'working_programs += 1')

# Extracurricular activity constraints:
research_writing_duration = Constraint('time', 'ticks = 15')
research_writing_activity = Constraint('writing', 'essays_written += 1')
research_programming_duration = Constraint('time', 'ticks = 15')
research_programming_activity = Constraint('development',
                                           'working_programs += 1')

# Obligations that responsibilities can be made from
essay_writing = Obligation([essay_deadline,
                            write_essay_constraint])
programming_assignment = Obligation([programming_deadline,
                                     write_code_constraint])
extra_writing = Obligation([research_writing_duration,
                            research_writing_activity])
extra_programming = Obligation([research_programming_duration,
                                research_programming_activity])


# Now we need to make something happen here.

# TODO: this model is going to move forward according to clock ticks. Should I
# be manually ticking the clock? Do my agents need to do anything to make that
# happen? Also, is it *possible* to manually tick the clock, or do I need to put
# in a workflow?

[global_clock.tick() for i in range(100)]
for lecturer in lecturers:
    lecturer.initiate_shutdown()

for student in students:
    student.initiate_shutdown()

global_clock.tick()

for lecturer in lecturers:
    lecturer.wait_for_shutdown()

for student in students:
    student.wait_for_shutdown()
