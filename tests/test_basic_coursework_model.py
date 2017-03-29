from resp_base import Obligation, Deadline, ResourceDelta
from resp_base import ResponsibilityEffect, Act
from resp_base import CourseworkWorkflow
from resp_base import ResponsibleAgent
from theatre_ag.theatre_ag import SynchronizingClock
import unittest


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
            student_workflow = CourseworkWorkflow()
            curr_student = ResponsibleAgent([], "student_"+str(i), self.global_clock, [CourseworkWorkflow()])

            # Create acts and effects to register with the student created here
            writing_effect = ResponsibilityEffect({'essays_written': 1})
            programming_effect = ResponsibilityEffect({'working_programs': 1})
            writing_act = Act(student_workflow.write_essay, student_workflow)
            programming_act = Act(student_workflow.write_program, student_workflow)

            # Register the acts
            curr_student.register_act(writing_effect, writing_act)
            curr_student.register_act(programming_effect, programming_act)

            curr_student.start()
            self.students.append(curr_student)

        # TODO: What notions should a lecturer have to begin with?

        self.lecturers = []
        for i in range(self.lecturer_count):
            curr_lecturer = ResponsibleAgent([], "lecturer_"+str(i), self.global_clock, [])
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
        programming_deadline = Deadline(10, self.global_clock)
        write_essay_constraint = ResourceDelta({'essays_written': 1})
        write_code_constraint = ResourceDelta({'working_programs': 1})

        # Extracurricular activity durations:
        research_writing_duration = Deadline(30, self.global_clock)
        research_programming_duration = Deadline(30, self.global_clock)

        # Obligations that responsibilities can be made from
        essay_writing = Obligation([essay_deadline,
                                    write_essay_constraint])
        programming_assignment = Obligation([programming_deadline,
                                             write_code_constraint])
        extra_writing = Obligation([research_writing_duration,
                                    write_essay_constraint])
        extra_programming = Obligation([research_programming_duration,
                                        write_code_constraint])

        with open('temp', 'a+') as temp:
            print(1, file=temp)
            # Now we need to make something happen here.
            for i in range(len(self.classes)):
                lecturer = self.lecturers[i]
                for student in self.classes[i]:
                    obligation = [essay_writing, programming_assignment][i%2]
                    lecturer.delegate_responsibility(obligation,
                                                        [0.75
                                                        for item in obligation.constraint_set],
                                                        student)
            print(2, file=temp)

            # Move five ticks forward
            for i in range(5):
                print('i: ' + str(i), file=temp)
                self.global_clock.tick()

            # Set alternative assignments
            for i in range(len(self.classes)):
                lecturer = self.lecturers[i]
                for student in self.classes[i]:
                    obligation = [essay_writing, programming_assignment][(i+1)%2]
                    lecturer.delegate_responsibility(obligation,
                                                        [0.75
                                                        for item in obligation.constraint_set],
                                                        student)

            print('ticking again', file=temp)
            [self.global_clock.tick() for i in range(10)]

            for student in self.students:
                self.assertTrue(student.essays_written == 1)



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
