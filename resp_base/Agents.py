from theatre_ag.theatre_ag import Actor as TheatreActor
from theatre_ag.theatre_ag.workflow import Idling as TheatreIdling
from theatre_ag.theatre_ag.workflow import treat_as_workflow, allocate_workflow_to
from theatre_ag.theatre_ag import default_cost
from theatre_ag.theatre_ag.task import Task
from theatre_ag.theatre_ag.actor import OutOfTurnsException
from .Responsibilities import Responsibility, ImportanceScoreSet, Obligation
from abc import ABCMeta, abstractmethod
from .utility_functions import mean, flatten, sign
from random import random, choice
from copy import copy
from time import sleep


class NotImplementedException(Exception):
    pass


class ResponsibleAgent(TheatreActor):

    responsible = True  # This will be a toggle for deactivating the formalism

    __metaclass__ = ABCMeta

    def __init__(self, notions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.responsibilities = copy(notions)  # Default beliefs about the world
        self.notions = copy(notions)
        self.consequential_responsibilities = []  # All discharged constraints

        # To be updated with the responsibility the current action represents
        self.current_responsibility = None

        # A responsible agent, when it has nothing to do, will pick another task
        # should it have one available. Otherwise, it will idle.
        self.idling = Idling()

        # An act is a bound method. self.acts is a dictionary of the form:
        #   {act: effect}
        # ..where the effect is a dictionary of expected resource changes.
        self.acts = {}
        self.register_acts()

        # Once we've got the acts, we need the act effect signs:
        self.acts_effect_signs = {}
        for act, effect in self.acts.items():
            self.acts_effect_signs[act] = dict(zip(effect.keys(),
                                                   [sign(value)
                                                    for value in effect.values()]
                                                   ))

    # TODO: This is deeply broken...
    def delegate_responsibility(self,
                                resp: Obligation,
                                importances: list,
                                delegee):  # Make this a ResponsibleAgent
        importance_score_set = ImportanceScoreSet(resp, importances)
        resp = Responsibility(importance_score_set, self, delegee)
        accepted = resp.delegee.accept_responsibility(resp)
        if not accepted:
            raise NotImplementedException("What happens if a responsibility \
                                          isn't allocated?")

    def interpret(self, resp):
        return resp

    def accept_responsibility(self, resp: Responsibility):
        #resp = self.interpret(resp)
        # TODO: fix this calculation
        accepted = mean(resp.importance_score_set.importances) > 0.5
        if accepted:
            self.responsibilities.append(resp)
            print('')
        print(accepted)
        return accepted

    def judge_degree_responsible(self, other_agent):
        c_resps = other_agent.consequential_responsibilities
        constraint_satisfactions = flatten(flatten(c_resps))
        constraints = {}

        # Filter constraints by type
        for outcome in constraint_satisfactions:
            if outcome.constraint_type not in constraints.keys():
                constraints[outcome.constraint_type] = []
            constraints[outcome.constraint_type].append(outcome)

        degree_responsible = {}
        # For each type, calculate the sum of the product of the outcome
        #   against its importance
        for constraint_type in constraints.keys():
            degree_responsible[constraint_type] = sum(
                [const.importance * const.outcome
                 for const in constraints[constraint_type]
                 ])

        # Return the dictionary of degrees of responsibility by type
        return degree_responsible

    def choose_action(self, responsibility):
        '''
        RETURNS: a function which returns a tuple (a,b):
            a: the success or failure of the discharge
            b: the set of constraint satisfactions (the consequential
            responsibility)
        Will choose the first action which seems to move resources in the intended
        direction.
        '''
        intended_effect = responsibility.calculate_effect()
        effect_signs = dict(zip(intended_effect.keys(),
                            [sign(value)
                             for value in intended_effect.values()]
                            ))
        for act, act_effect_signs in self.acts_effect_signs.items():
            if effect_signs == act_effect_signs:
                return act
        return self.idling.idle

    def choose_responsibility(self):
        '''
        Choose a responsibility with the highest average importance across various
        factors.
        TODO: make this smarter! Just taking the mean doesn't take into account
            the nature of the importances.
        TODO: Consider deadlines! Implement an eisenhower matrix, to weigh
            importance against urgency?
        '''
        resps = copy(self.responsibilities)
        resps = [resp for resp in resps if resp not in self.notions]
        resp = max(resps,
                   key=lambda x: mean(x.importance_score_set.importances))
        return resp

    # Selects a responsibility to discharge, attempts to discharge it, and
    # modifies the list of responsibilities accordingly.
    def discharge(self):
        anything_to_discharge = len(self.responsibilities) > 0
        if anything_to_discharge:
            resp_chosen = self.choose_responsibility()
            self.current_responsibility = resp_chosen
            discharge_function = self.choose_action(resp_chosen)
            discharged_successfully, constraint_satisfactions = \
                discharge_function()
            self.consequential_responsibilities.append(constraint_satisfactions)
            if discharged_successfully:
                self.responsibilities.remove(resp_chosen)
        return anything_to_discharge

    def next_action(self):
        anything_to_discharge =\
                len(self.responsibilities) - len(self.notions) > 0
        if anything_to_discharge:
            resp_chosen = self.choose_responsibility()
            self.current_responsibility = resp_chosen
            discharge_function = self.choose_action(resp_chosen)
        else:
            discharge_function = self.idling.idle
        return discharge_function

    def perform(self):
        '''
        Allows an agent to act on each tick.
        TODO: Add responsibilities to the task queue?
        '''
        while self.wait_for_directions:
            try:
                currently_idling = False
                if self.responsibilities == self.notions:
                    next_action = self.idling.idle
                    workflow = self.idling
                    task = Task(workflow, next_action)
                    currently_idling = True
                else:
                    print('discharging a responsibility')
                    next_action = self.next_action()
                    print(next_action.__name__)
                    exec('DummyWorkflow.'+next_action.__name__+' = next_action')
                    workflow = DummyWorkflow()
                    task = Task(workflow, next_action)
                    entry_point_name = task.entry_point.__name__
                    allocate_workflow_to(self, task.workflow)
                    task.entry_point = task.workflow.__getattribute__(entry_point_name)

                    treat_as_workflow(DummyWorkflow)

                    duration = \
                        self.current_responsibility.calculate_effect()['duration']
                    next_action = default_cost(duration)(next_action)

                self.current_task = task

                self._task_history.append(task)
                self.current_task = task
                result = task.entry_point(*task.args)
                if result is not None:
                    discharged_successfully, constraint_satisfactions = result
                    self.consequential_responsibilities.append(constraint_satisfactions)
                    if discharged_successfully:
                        self.responsibilities.remove(self.current_responsibility)
                        self.current_responsibility = None

                    # Choose a next action; this one's finished!
                    self.wait_for_directions = True
                elif currently_idling:
                    self.wait_for_directions = True
                else:
                    self.wait_for_directions = False

            except OutOfTurnsException:
                break

        # Ensure that clock can proceed for other listeners.
        self.clock.remove_tick_listener(self)
        self.waiting_for_tick.set()

    @abstractmethod
    def register_acts(self):
        pass


# TODO: Update with any lecturer-specific actions.
# Lecturers exhibit primarily delegating behaviour!
class Lecturer(ResponsibleAgent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # There must be an attribute for every resource which can be effected as
        # the result of a Constraints.ResourceDelta being discharged.
        self.essays_written = 0

    # Lecturers can write essays
    # (We're calling papers essays, so as to simplify the model's ontology.)
    # RETURNS: tuple (a,b):
    #     a: success bool
    #     b: set of constraints with pass/failure
    # TODO: Better done with fuzzimoss?
    def write_essay(self, resp):
        written_successfully = (random() > 0.1)
        if written_successfully:
            self.essays_written += 1
            # Essay writing responsibilities have deadlines and essay details
            for i in range(len(resp.obligation.constraint_set)):
                resp.obligation.constraint_set[i].record_outcome(True)
        else:
            # Fail to write an essay one in ten times
            for i in range(len(resp.obligation.constraint_set)):
                resp.obligation.constraint_set[i].record_outcome(True)
            # One constraint will have failed.
            failed_responsibility = choice(
                range(len(resp.obligation.constraint_set)))
            resp.obligation.constraint_set[
                failed_responsibility].record_outcome(False)
        return (written_successfully, resp.obligation.constraint_set)

    def write_program(self, resp):
        written_successfully = (random() > 0.1)
        if written_successfully:
            self.working_programs += 1
            # Essay writing responsibilities have deadlines and essay details
            for i in range(len(resp.obligation.constraint_set)):
                resp.obligation.constraint_set[i].record_outcome(True)
        else:
            # Fail to write an essay one in ten times
            for i in range(len(resp.obligation.constraint_set)):
                resp.obligation.constraint_set[i].record_outcome(True)
            # One constraint will have failed.
            failed_responsibility = choice(
                range(len(resp.obligation.constraint_set)))
            resp.obligation.constraint_set[
                failed_responsibility].record_outcome(False)

    def register_acts(self):
        self.acts[self.write_essay] = {'essays_written': 1}
        self.acts[self.write_program] = {'working_programs': 1}


# TODO: Update with any student-specific actions.
# Students exhibit primarily discharging behaviour!
class Student(ResponsibleAgent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # There must be an attribute for every resource which can be effected as
        # the result of a Constraints.ResourceDelta being discharged.
        self.essays_written = 0

    # Students can write essays
    # RETURNS: tuple (a,b):
    #     a: success bool
    #     b: set of constraints with pass/failure
    # TODO: Better done with fuzzimoss?
    def write_essay(self, resp):
        written_successfully = (random() > 0.1)
        if written_successfully:
            self.essays_written += 1
            # Essay writing responsibilities have deadlines and essay details
            for i in range(len(resp.obligation.constraint_set)):
                resp.obligation.constraint_set[i].record_outcome(True)
        else:
            # Fail to write an essay one in ten times
            for i in range(len(resp.obligation.constraint_set)):
                resp.obligation.constraint_set[i].record_outcome(True)
            # One constraint will have failed.
            failed_responsibility = choice(
                range(len(resp.obligation.constraint_set)))
            resp.obligation.constraint_set[
                failed_responsibility].record_outcome(False)
        return (written_successfully, resp.obligation.constraint_set)

    def write_program(self, resp):
        written_successfully = (random() > 0.1)
        if written_successfully:
            self.working_programs += 1
            # Essay writing responsibilities have deadlines and essay details
            for i in range(len(resp.obligation.constraint_set)):
                resp.obligation.constraint_set[i].record_outcome(True)
        else:
            # Fail to write an essay one in ten times
            for i in range(len(resp.obligation.constraint_set)):
                resp.obligation.constraint_set[i].record_outcome(True)
            # One constraint will have failed.
            failed_responsibility = choice(
                range(len(resp.obligation.constraint_set)))
            resp.obligation.constraint_set[
                failed_responsibility].record_outcome(False)

    def register_acts(self):
        self.acts[self.write_essay] = {'essays_written': 1}
        self.acts[self.write_program] = {'working_programs': 1}


class Idling(TheatreIdling):
    # TODO: make this default to
    pass

class DummyWorkflow:
    is_workflow = True

treat_as_workflow(DummyWorkflow)
