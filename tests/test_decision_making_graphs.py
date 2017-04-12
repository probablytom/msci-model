from resp_base import Obligation, Deadline, ResourceDelta, ResponsibilityEffect, Act, mean, BullshitAgent
from resp_base import CourseworkWorkflow, IncompetentCourseworkWorkflow, HedonisticAgent, StudiousAgent, Lecturer
from theatre_ag.theatre_ag import SynchronizingClock
from random import choice, seed
import matplotlib.pyplot as plt
from copy import copy
import unittest


class TestTaskSelectionGraphs(unittest.TestCase):

    def manualSetUp(self,
                    max_ticks=100,
                    number_of_agents=7):
        self.global_clock = SynchronizingClock(max_ticks=max_ticks)
        self.lecturer_count = 1
        self.student_count = number_of_agents  # (per type of student)

        self.students = []
        self.lecturers = []

        # Construct students
        for i in range(self.student_count):
            for type_of_student in [HedonisticAgent, StudiousAgent, BullshitAgent]:
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


    def trial(self,
              complete_ticks=True,
              number_of_agents=7,
              max_ticks=100):
        seed(0)
        self.manualSetUp(max_ticks, number_of_agents)
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

        if complete_ticks:
            self.global_clock.tick_toc()


    def test_competence_delta(self):
        # Competent agents should be judged as more responsible than less competent agents
        self.trial(max_ticks=150,
                   complete_ticks=False)
        lecturer = self.lecturers[0]
        ticks = 0
        judgements = {'competent': [],
                      'incompetent': []}
        while ticks < 150:
            ticks += 15
            [self.global_clock.tick() for i in range(15)]
            judgements['competent'].append(mean([lecturer.general_responsibility_judgement(student)
                                                 for student in self.students
                                                 if type(student.workflows[0]) is CourseworkWorkflow and
                                                 type(student) is StudiousAgent]))
            judgements['incompetent'].append(mean([lecturer.general_responsibility_judgement(student)
                                                 for student in self.students
                                                 if type(student.workflows[0]) is IncompetentCourseworkWorkflow and
                                                 type(student) is StudiousAgent]))
        plt.plot(range(15, 151, 15), judgements['competent'], 'bs',
                 range(15, 151, 15), judgements['incompetent'], 'g^')
        plt.xlabel('ticks')
        plt.ylabel('average general responsibility judgement')
        plt.savefig('test_competence_delta.svg')
        # self.assertTrue(competent_judgement_average > incompetent_judgement_average)

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
        number_excellent_students_selected_responsibly = []
        number_excellent_students_selected_randomly = []
        for i in range(10):
            print(i)
            # Select agents for task allocation according to their responsibility
            allocated_agents = [[], []]
            self.trial(max_ticks=150,
                       complete_ticks=False)
            lecturer = self.lecturers[0]
            for i in range(10):
                [self.global_clock.tick() for i in range(15)]
                best_student_chosen = max(self.students,
                                          key=lambda x: lecturer.specific_responsibility_judgement(x, 'essays_written'))
                allocated_agents[0].append(best_student_chosen)
            self.tearDown()

            # Select agents for task allocation randomly
            self.trial(max_ticks=150,
                       complete_ticks=False)
            lecturer = self.lecturers[0]
            for i in range(10):
                [self.global_clock.tick() for i in range(15)]
                student_chosen = choice(self.students)
                allocated_agents[1].append(student_chosen)
            self.tearDown()

            # Students chosen responsibly should be more studious and more competent.
            number_excellent_students_selected_responsibly.append(len([student for student in allocated_agents[0]
                                                                  if type(student.workflows[0]) == CourseworkWorkflow and \
                                                                  student.__class__ == StudiousAgent]))
            number_excellent_students_selected_randomly.append(len([student for student in allocated_agents[1]
                                                               if type(student.workflows[0]) == CourseworkWorkflow and \
                                                               student.__class__ == StudiousAgent]))

        print(number_excellent_students_selected_responsibly, number_excellent_students_selected_randomly)

        plt.plot(range(15,151,15), number_excellent_students_selected_responsibly, 'bs',
                 range(15,151,15), number_excellent_students_selected_randomly, 'g^')
        plt.ylabel('number of excellent students selected')
        plt.xlabel('number of ticks')
        plt.show()

        self.assertTrue(number_excellent_students_selected_responsibly > number_excellent_students_selected_randomly)

    def test_responsibility_directs_behaviour(self):
        bullshit_judgements = []
        responsible_judgements = []
        hedonistic_judgements = []
        self.trial(max_ticks=150,
                   complete_ticks=False)
        lecturer = self.lecturers[0]
        for i in range(10):
            [self.global_clock.tick() for i in range(15)]
            bullshit_judgements.append(mean([lecturer.general_responsibility_judgement(student)
                                             for student in self.students
                                             if type(student) is BullshitAgent]))
            responsible_judgements.append(mean([lecturer.general_responsibility_judgement(student)
                                                for student in self.students
                                                if type(student) is StudiousAgent]))
            hedonistic_judgements.append(mean([lecturer.general_responsibility_judgement(student)
                                               for student in self.students
                                               if type(student) is HedonisticAgent]))
        self.tearDown()
        plt.plot(range(15,151,15), responsible_judgements, 'bs',
                 range(15,151,15), hedonistic_judgements, 'rs',
                 range(15,151,15), bullshit_judgements, 'g^')
        plt.xlabel('ticks')
        plt.ylabel('mean degree generally responsible')
        plt.savefig('test_responsibility_directs_behaviour.svg')

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
