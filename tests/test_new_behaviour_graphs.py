from resp_base import Obligation, Deadline, ResourceDelta, ResponsibilityEffect, Act, mean, BullshitAgent
from resp_base import CourseworkWorkflow, IncompetentCourseworkWorkflow, HedonisticAgent, StudiousAgent, Lecturer
from theatre_ag.theatre_ag import SynchronizingClock
import matplotlib.pyplot as plt
from random import seed
from copy import copy
import unittest


class TestBehaviourGraphs(unittest.TestCase):

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


    def test_adopting_new_behaviour(self):
        gradual_trial_results = []
        number_of_trials = 10
        number_of_ticks = 0
        while number_of_ticks < 150:
            trial_results = [[], []]
            number_of_ticks += 15

            # A set of trials where lecturers advise bad students
            for i in range(number_of_trials):
                self.trial(complete_ticks=False,
                           max_ticks=number_of_ticks)
                lecturer = self.lecturers[0]

                while self.global_clock.current_tick < self.global_clock.max_ticks/2:
                    self.global_clock.tick()

                for student in self.students:
                    if lecturer.general_responsibility_judgement(student) < lecturer.basic_judgement_responsible:
                        lecturer.advise(student)

                self.global_clock.tick_toc()

                trial_results[0].append(mean([lecturer.general_responsibility_judgement(student)
                                              for student in self.students]))

                self.tearDown()
            print(number_of_ticks)
            trial_results[0] = mean(trial_results[0])

            # A set of trials where lecturers do not advise
            for i in range(number_of_trials):
                self.trial(complete_ticks=True,
                           max_ticks=number_of_ticks)
                lecturer = self.lecturers[0]
                trial_results[1].append(mean([lecturer.general_responsibility_judgement(student)
                                              for student in self.students]))

            trial_results[1] = mean(trial_results[1])
            gradual_trial_results.append(trial_results)
            print(number_of_ticks)

        print(gradual_trial_results)

        plt.plot(range(15, 151, 15), [trial[0] for trial in gradual_trial_results], 'bs',
                 range(15, 151, 15), [trial[1] for trial in gradual_trial_results], 'g^')
        plt.xlabel('Number of ticks')
        plt.ylabel('Average degree of general responsibleness over 10 ticks')
        plt.show()

        # If the experiment is successful, results from the trials involving advice should result in more responsible
        #  ...agents overall, because their responsibility is directed by advice via the formalism's interpretation
        #  ...factors.
        self.assertTrue(mean(trial_results[0]) > mean(trial_results[1]))

