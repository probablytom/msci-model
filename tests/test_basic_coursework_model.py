from resp_base import Obligation, Deadline, ResourceDelta, ResponsibilityEffect, Act, BasicResponsibleAgent
from resp_base import CourseworkWorkflow, IncompetentCourseworkWorkflow, LazyAgent, HedonisticAgent, StudiousAgent
from theatre_ag.theatre_ag import SynchronizingClock
import unittest


class TestCourseworkModel(unittest.TestCase):

    def setUp(self):
        self.global_clock = SynchronizingClock(max_ticks=100)
        self.lecturer_count = 1
        self.student_count = 7  # (per type of student)

        self.students = []
        self.lecturers = []

        # Construct students
        for i in range(self.student_count):
            for type_of_student in [LazyAgent, HedonisticAgent, StudiousAgent]:
                for competence in [CourseworkWorkflow, IncompetentCourseworkWorkflow]:
                    student_workflow = competence()
                    curr_student = type_of_student([],
                                                   "student_"+str(len(self.students)),
                                                   self.global_clock,
                                                   [student_workflow])

                    # Create acts and effects to register with the student created here
                    writing_effect = ResponsibilityEffect({'essays_written': 1})
                    programming_effect = ResponsibilityEffect({'working_programs': 1})
                    writing_act = Act(writing_effect,
                                      student_workflow.write_essay,
                                      student_workflow)
                    programming_act = Act(programming_effect,
                                          student_workflow.write_program,
                                          student_workflow)

                    # Register the acts
                    curr_student.register_act(writing_act)
                    curr_student.register_act(programming_act)

                    curr_student.start()
                    self.students.append(curr_student)


        # Construct lecturers
        for i in range(self.lecturer_count):
            curr_lecturer = BasicResponsibleAgent([], "lecturer_"+str(i), self.global_clock, [])
            curr_lecturer.start()
            self.lecturers.append(curr_lecturer)

    def test_model_basic(self):
        essay_deadline = Deadline(10, self.global_clock)
        programming_deadline = Deadline(10, self.global_clock)
        relax_deadline = Deadline(2, self.global_clock)
        write_essay_constraint = ResourceDelta({'essays_written': 1})
        write_code_constraint = ResourceDelta({'working_programs': 1})
        relax_constraint = ResourceDelta({'personal_enjoyment': 1})

        # Extracurricular activity durations:
        research_writing_duration = Deadline(5, self.global_clock)
        research_programming_duration = Deadline(5, self.global_clock)

        # Obligations that responsibilities can be made from
        essay_writing = Obligation([essay_deadline,
                                    write_essay_constraint])
        programming_assignment = Obligation([programming_deadline,
                                             write_code_constraint])
        extra_writing = Obligation([research_writing_duration,
                                    write_essay_constraint])
        extra_programming = Obligation([research_programming_duration,
                                        write_code_constraint])
        relaxation = Obligation([relax_constraint, relax_deadline])

        # Give all students a writing and programming assignment.
        lecturer = self.lecturers[0]
        for student in self.students:
            lecturer.delegate_responsibility(programming_assignment,
                                             [0.75
                                              for item in programming_assignment.constraint_set],
                                             student)
            lecturer.delegate_responsibility(essay_writing,
                                             [0.75
                                              for item in essay_writing.constraint_set],
                                             student)

        for i in range(22):
            self.global_clock.tick()

        # All students should have written essays and programs, because no responsibility to relax is set.
        for student in self.students:
                self.assertTrue(student.get_sociotechnical_state('working_programs') == 1)
                self.assertTrue(student.get_sociotechnical_state('essays_written') == 1)


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
