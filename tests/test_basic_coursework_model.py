from resp_base import Student, Lecturer, Obligation, Deadline, ResourceDelta
from theatre_ag.theatre_ag import SynchronizingClock
import unittest
from copy import copy
from time import sleep


class TestCourseworkModel(unittest.TestCase):

    def setUp(self):
        # TODO: What's the model duration?
        self.global_clock = SynchronizingClock(max_ticks=100)
        self.lecturer_count = 3
        self.student_count = 7
        self.semester_size = 3  # classes per student

        # Create a bunch of self.lecturers and self.students.
        # TODO: What notions should a student have to begin with?

        self.students = []
        for i in range(self.student_count):
            curr_student = Student([], "student_"+str(i), self.global_clock)
            curr_student.start()
            self.students.append(curr_student)

        # TODO: What notions should a lecturer have to begin with?

        self.lecturers = []
        for i in range(self.lecturer_count):
            curr_lecturer = Lecturer([], "lecturer_"+str(i), self.global_clock)
            curr_lecturer.start()
            self.lecturers.append(curr_lecturer)

        # We'll need some classes -- just collections of students
        self.classes = [[]] * self.lecturer_count  # A class for every lecturer

        # Should we randomise class allocation?
        for i in range(self.student_count * self.semester_size):
                self.classes[i % self.lecturer_count].append(
                        self.students[i % self.student_count])

    def test_model_basic(self):
        # TODO: What's the best way to encode the constraint text?
        essay_deadline = Deadline(10, self.global_clock)
        print(1)
        programming_deadline = Deadline(10, self.global_clock)
        print(2)
        write_essay_constraint = ResourceDelta({'essays_written': 1})
        print(3)
        write_code_constraint = ResourceDelta({'working_programs': 1})

        # Extracurricular activity durations:
        research_writing_duration = Deadline(30, self.global_clock)
        research_programming_duration = Deadline(30, self.global_clock)

        # Obligations that responsibilities can be made from
        print(4)
        essay_writing = Obligation([essay_deadline,
                                    write_essay_constraint])
        programming_assignment = Obligation([programming_deadline,
                                             write_code_constraint])
        extra_writing = Obligation([research_writing_duration,
                                    write_essay_constraint])
        extra_programming = Obligation([research_programming_duration,
                                        write_code_constraint])

        print(5)
        # Now we need to make something happen here.
        for i in range(len(self.classes)):
            print('i: ' + str(i))
            lecturer = self.lecturers[i]
            for student in self.classes[i]:
                obligation = [essay_writing, programming_assignment][i%2]
                lecturer.delegate_responsibility(obligation,
                                                    [0.75
                                                    for item in obligation.constraint_set],
                                                    student)

        # Move five ticks forward
        for i in range(5):
            print('trying to tick...')
            self.global_clock.tick()
            print('just ticked...')

        # Set alternative assignments
        for i in range(len(self.classes)):
            lecturer = self.lecturers[i]
            for student in self.classes[i]:
                obligation = [essay_writing, programming_assignment][(i+1)%2]
                lecturer.delegate_responsibility(obligation,
                                                    [0.75
                                                    for item in obligation.constraint_set],
                                                    student)

        [self.global_clock.tick() for i in range(10)]

        for student in self.students:
            print(student.consequential_responsibilities)


    def tearDown(self):
        for lecturer in self.lecturers:
            lecturer.initiate_shutdown()

        for student in self.students:
            student.initiate_shutdown()

        self.global_clock.tick()

        for lecturer in self.lecturers:
            lecturer.wait_for_shutdown()

        for student in self.students:
            student.wait_for_shutdown()
