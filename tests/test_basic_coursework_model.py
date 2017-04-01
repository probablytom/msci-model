from resp_base import Obligation, Deadline, ResourceDelta, ResponsibilityEffect, Act, BasicResponsibleAgent
from functools import reduce
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
        write_essay_constraint = ResourceDelta({'essays_written': 1})
        write_code_constraint = ResourceDelta({'working_programs': 1})

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

        # Give all students a writing and programming assignment.
        lecturer = self.lecturers[0]
        for student in self.students:
            lecturer.delegate_responsibility(essay_writing,
                                             [0.75
                                              for item in programming_assignment.constraint_set],
                                             student)
            lecturer.delegate_responsibility(programming_assignment,
                                             [0.4
                                              for item in programming_assignment.constraint_set],
                                             student)

        for i in range(int(self.global_clock.max_ticks/2)):
            self.global_clock.tick()

        for student in self.students:
            lecturer.delegate_responsibility(essay_writing,
                                             [0.3
                                              for item in programming_assignment.constraint_set],
                                             student)
            lecturer.delegate_responsibility(programming_assignment,
                                             [0.3
                                              for item in programming_assignment.constraint_set],
                                             student)

        self.global_clock.tick_toc()

        def dict_sum(dict_1, dict_2):
            for element, value in dict_1.items():
                if dict_2.get(element) is None:
                    dict_2[element] = value
                else:
                    dict_2[element] += value
            return dict_2

        # All students should have written essays and programs, because no responsibility to relax is set.
        results = {}
        for student in self.students:
            if results.get((type(student), type(student.workflows[0]))) is None:
                results[(type(student), type(student.workflows[0]))] = {}
            curr_result = results[(type(student), type(student.workflows[0]))]
            results[(type(student), type(student.workflows[0]))] = dict_sum(curr_result,
                                                                        student.socio_states)

        # Lazy agents should write fewer essays on average than studious agents, regardless of competence.
        def results_of_agents(agent_type):
            results_for_agent = [result
                                 for (agent_class, workflow_class), result in results.items()
                                 if agent_type in [agent_class, workflow_class]]
            return len(results_for_agent), reduce(dict_sum, results_for_agent)

        no_hedonistic_agents, hedonistic_agent_results = results_of_agents(HedonisticAgent)
        no_hedonistic_agents *= 7
        no_studious_agents, studious_agent_results = results_of_agents(StudiousAgent)
        no_studious_agents *= 7

        hedonistic_essay_average = hedonistic_agent_results.get('essays_written', 0) / no_hedonistic_agents
        studious_essay_average = studious_agent_results.get('essays_written', 0) / no_studious_agents
        print(hedonistic_essay_average, studious_essay_average)
        self.assertTrue(studious_essay_average > hedonistic_essay_average)

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
