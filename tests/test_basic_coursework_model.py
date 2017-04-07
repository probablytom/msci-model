from resp_base import Obligation, Deadline, ResourceDelta, ResponsibilityEffect, Act, mean
from resp_base import CourseworkWorkflow, IncompetentCourseworkWorkflow, HedonisticAgent, StudiousAgent, Lecturer
from theatre_ag.theatre_ag import SynchronizingClock
from random import choice, seed
from copy import copy
import unittest


class TestCourseworkModel(unittest.TestCase):

    def manualSetUp(self):
        self.global_clock = SynchronizingClock(max_ticks=500)
        self.lecturer_count = 1
        self.student_count = 7  # (per type of student)

        self.students = []
        self.lecturers = []

        # Construct students
        for i in range(self.student_count):
            for type_of_student in [HedonisticAgent, StudiousAgent]:
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
            curr_lecturer = Lecturer([], "lecturer_"+str(i), self.global_clock, [])
            curr_lecturer.start()
            self.lecturers.append(curr_lecturer)


    def trial(self):
        seed(0)
        self.manualSetUp()
        lecturer = self.lecturers[0]
        # Give all students a writing and programming assignment.
        for student in self.students:
            for i in range(10):
                essay_deadline = Deadline(10, self.global_clock)
                programming_deadline = Deadline(10, self.global_clock)
                visit_concert_duration = Deadline(20, self.global_clock)
                write_essay_constraint = ResourceDelta({'essays_written': 1})
                write_code_constraint = ResourceDelta({'working_programs': 1})
                visit_concert_effect = ResourceDelta({'personal_enjoyment': 1})


                # Obligations that responsibilities can be made from
                essay_writing = Obligation([essay_deadline,
                                            write_essay_constraint],
                                           name="write essay")
                programming_assignment = Obligation([programming_deadline,
                                                     write_code_constraint],
                                                    name="write program")
                visit_concert = Obligation([visit_concert_duration,
                                            visit_concert_effect],
                                           name="visit concert")
                lecturer.delegate_responsibility(copy(essay_writing),
                                                 [i * 0.075
                                                  for item in essay_writing.constraint_set],
                                                 student)

                lecturer.delegate_responsibility(copy(programming_assignment),
                                                 [i * 0.075
                                                  for item in programming_assignment.constraint_set],
                                                 student)

                lecturer.delegate_responsibility(copy(visit_concert),
                                                 [i * 0.075
                                                  for item in visit_concert.constraint_set],
                                                 student)

        self.global_clock.tick_toc()


    def test_competence_delta(self):
        # Competent agents should be judged as more responsible than less competent agents
        self.trial()
        lecturer = self.lecturers[0]
        competent_judgement_average = mean([lecturer.general_responsibility_judgement(student)
                                            for student in self.students
                                            if type(student.workflows[0]) is CourseworkWorkflow])
        incompetent_judgement_average = mean([lecturer.general_responsibility_judgement(student)
                                            for student in self.students
                                            if type(student.workflows[0]) is IncompetentCourseworkWorkflow])
        self.assertTrue(competent_judgement_average > incompetent_judgement_average)

    def test_agent_type_delta(self):
        # Different types of agents should write different numbers of essays
        self.trial()
        studious_essay_average = mean([student.socio_states.get('essays_written', 0)
                                       for student in self.students
                                       if type(student) is StudiousAgent])
        hedonistic_essay_average = mean([student.socio_states.get('essays_written', 0)
                                       for student in self.students
                                       if type(student) is HedonisticAgent])
        self.assertTrue(studious_essay_average > hedonistic_essay_average)

    def test_allocation_by_responsibility(self):
        allocated_agents = []
        for i in range(10):
            self.trial()
            lecturer = self.lecturers[0]

            best_student_chosen = max(self.students,
                                      key=lambda x: lecturer.specific_responsibility_judgement(x, 'essays_written'))
            allocated_agents.append(best_student_chosen)
            self.tearDown()

        number_competent_agents_chosen = len([student for student in allocated_agents
                                              if type(student.workflows[0]) is CourseworkWorkflow])
        number_incompetent_agents_chosen = len([student for student in allocated_agents
                                                if type(student.workflows[0]) is IncompetentCourseworkWorkflow])

        self.assertTrue(number_competent_agents_chosen > number_incompetent_agents_chosen)

    def test_compare_responsible_allocation_to_standard(self):
        allocated_agents = [[], []]
        # Select agents for task allocation according to their responsibility
        for i in range(10):
            self.trial()
            lecturer = self.lecturers[0]
            best_student_chosen = max(self.students,
                                      key=lambda x: lecturer.specific_responsibility_judgement(x, 'essays_written'))
            student_rankings = [(lecturer.specific_responsibility_judgement(student, 'essays_written'), student)
                                for student in sorted(self.students,
                                                      key=lambda x: lecturer.specific_responsibility_judgement(x, 'essays_written'))[::-1]]
            allocated_agents[0].append(best_student_chosen)
            print(type(best_student_chosen), type(best_student_chosen.workflows[0]))
            self.tearDown()

        # Select agents for task allocation randomly
        for i in range(10):
            self.trial()
            lecturer = self.lecturers[0]
            student_chosen = choice(self.students)
            allocated_agents[1].append(student_chosen)
            self.tearDown()

        # Students chosen responsibly should be more studious and more competent.
        number_excellent_students_selected_responsibly = len([student for student in allocated_agents[0]
                                                              if type(student.workflows[0]) == CourseworkWorkflow and\
                                                              student.__class__ == StudiousAgent])
        number_excellent_students_selected_randomly = len([student for student in allocated_agents[1]
                                                              if type(student.workflows[0]) == CourseworkWorkflow and \
                                                              student.__class__ == StudiousAgent])

        print(number_excellent_students_selected_responsibly, number_excellent_students_selected_randomly)

        self.assertTrue(number_excellent_students_selected_responsibly > number_excellent_students_selected_randomly)


    def tearDown(self):
        try:
            for lecturer in self.lecturers:
                lecturer.initiate_shutdown()

            for student in self.students:
                student.initiate_shutdown()

            self.global_clock.tick()

            for lecturer in self.lecturers:
                lecturer.wait_for_shutdown()

            for student in self.students:
                student.wait_for_shutdown()
        except:
            pass
