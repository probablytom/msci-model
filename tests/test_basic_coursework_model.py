from resp_base import Student, Lecturer, Obligation, Deadline, Coursework_Body
from theatre_ag import SynchronizingClock
import unittest


class TestCourseworkModel(unittest.TestCase):

    def setUp(self):
        # TODO: What's the model duration?
        self.global_clock = SynchronizingClock(max_ticks=100)
        self.lecturer_count = 5
        self.student_count = 20
        self.semester_size = 3  # classes per student

        # Create a bunch of self.lecturers and self.students.
        # TODO: What notions should a student have to begin with?

        self.students = []
        for i in range(student_count):
            curr_student = Student([], "student_"+str(i), self.global_clock)
            curr_student.start()
            self.students.append(curr_student)

        # TODO: What notions should a lecturer have to begin with?

        self.lecturers = []
        for i in range(lecturer_count):
            curr_lecturer = Lecturer([], "lecturer_"+str(i), self.global_clock)
            curr_lecturer.start()
            self.lecturers.append(curr_lecturer)

        # We'll need some classes -- just collections of students
        self.classes = [[]] * lecturer_count  # A class for every lecturer

        # Should we randomise class allocation?
        for i in range(student_count * semester_size):
                self.classes[i % lecturer_count].append(
                        self.students[i % student_count])

    def test_model_basic(self):
        # TODO: What's the best way to encode the constraint text?
        essay_deadline = Deadline('time',
                                  {'duration': 10},
                                  self.global_clock)
        programming_deadline = Deadline('time',
                                        {'duration': 10},
                                        self.global_clock)
        write_essay_constraint = Coursework_Body('writing',
                                                 {'essays_written':
                                                         '+1'})
        write_code_constraint = Coursework_Body('development',
                                                {'working_programs':
                                                        '+1'})

        # Extracurricular activity constraints:
        research_writing_duration = Deadline('time',
                                             {'duration': 10},
                                             self.global_clock)
        research_programming_duration = Deadline('time',
                                                 {'duration': 10},
                                                 self.global_clock)
        research_writing_activity = Coursework_Body('writing',
                                                    {'essays_written':
                                                            '+1'})
        research_programming_activity = Coursework_Body('development',
                                                        {'working_programs':
                                                             '+1'})

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
