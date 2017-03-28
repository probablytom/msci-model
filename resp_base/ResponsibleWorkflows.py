from theatre_ag.theatre_ag.workflow import treat_as_workflow
from theatre_ag.theatre_ag import default_cost
from theatre_ag.theatre_ag.task import Task
from .Responsibilities import Responsibility, ImportanceScoreSet, Obligation
from abc import ABCMeta, abstractmethod
from .utility_functions import mean, flatten, sign
from random import random, choice
from copy import copy


class ResponsibleAgentWorkflow(object):

    responsible = True  # This will be a toggle for deactivating the formalism

    __metaclass__ = ABCMeta

    def __init__(self, notions, *args, **kwargs):
        self.responsibilities = copy(notions)  # Default beliefs about the world
        self.notions = copy(notions)
        self.consequential_responsibilities = []  # All discharged constraints

        # To be updated with the responsibility the current action represents
        self.current_responsibility = None

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
            raise NotImplemented("What happens if a responsibility \
                                  isn't allocated?")

    def interpret(self, resp):
        return resp

    def accept_responsibility(self, resp: Responsibility):
        #resp = self.interpret(resp)
        # TODO: fix this calculation
        accepted = mean(resp.importance_score_set.importances) > 0.5
        if accepted:
            self.responsibilities.append(resp)
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
        intended_effect.pop('duration')
        effect_signs = dict(zip(intended_effect.keys(),
                                [sign(value)
                                 for value in intended_effect.values()]
                                ))
        for act, act_effect_signs in self.acts_effect_signs.items():
            if effect_signs == act_effect_signs:
                return act
        return self.agent.idling.idle

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
        if resps == []:
            return None
        else:
            return max(resps,
                       key=lambda x: mean(x.importance_score_set.importances))

    def next_action(self):
        resp_chosen = self.choose_responsibility()
        if resp_chosen is not None:
            self.current_responsibility = resp_chosen
            discharge_function = self.choose_action(resp_chosen)
        else:
            discharge_function = self.agent.idling.idle
        return discharge_function

    def get_next_task(self):
        # Get the next action
        next_action = self.next_action()

        # Depending on whether the next action is to idle or is a free
        # action, act accordingly.
        if next_action.__name__ is not 'idle':
            # Add its duration
            duration = \
                self.current_responsibility.calculate_effect()['duration']
            #next_action.reference_function.default_cost = 1
            workflow = self

        else:
            # We're idling
            workflow = self.agent.idling

        # Create and return the relevant task
        task = Task(workflow, next_action)
        return task

    def handle_return_value(self, return_value):
        if return_value is not None:
            discharged_successfully, constraint_satisfactions = return_value
            self.consequential_responsibilities.append(constraint_satisfactions)
            if discharged_successfully:
                self.responsibilities.remove(self.current_responsibility)
                self.current_responsibility = None

    # Lecturers can write essays
    # (We're calling papers essays, so as to simplify the model's ontology.)
    # RETURNS: tuple (a,b):
    #     a: success bool
    #     b: set of constraints with pass/failure
    @default_cost(1)
    def write_essay(self):
        written_successfully = (random() > 0.1)
        written_successfully = True
        if written_successfully:
            self.essays_written += 1
            # Essay writing responsibilities have deadlines and essay details
            for i in range(len(self.current_responsibility.importance_score_set.constraints)):
                self.current_responsibility.importance_score_set.constraints[i].record_outcome(True)
        else:
            # Fail to write an essay one in ten times
            for i in range(len(self.current_responsibility.importance_score_set.constraints)):
                self.current_responsibility.importance_score_set.constraints[i].record_outcome(True)
            # One constraint will have failed.
            failed_responsibility = choice(
                range(len(self.current_responsibility.importance_score_set.constraints)))
            self.current_responsibility.importance_score_set.constraints[
                failed_responsibility].record_outcome(False)
        return (written_successfully, self.current_responsibility.importance_score_set.constraints)

    @default_cost(1)
    def write_program(self):
        written_successfully = (random() > 0.1)
        written_successfully = True
        if written_successfully:
            self.working_programs += 1
            # Essay writing responsibilities have deadlines and essay details
            for i in range(len(self.current_responsibility.importance_score_set.constraints)):
                self.current_responsibility.importance_score_set.constraints[i].record_outcome(True)
        else:
            # Fail to write an essay one in ten times
            for i in range(len(self.current_responsibility.importance_score_set.constraints)):
                self.current_responsibility.importance_score_set.constraints[i].record_outcome(True)
            # One constraint will have failed.
            failed_responsibility = choice(
                range(len(self.current_responsibility.importance_score_set.constraints)))
            self.current_responsibility.importance_score_set.constraints[
                failed_responsibility].record_outcome(False)


    @abstractmethod
    def register_acts(self):
        pass


# TODO: Update with any lecturer-specific actions.
# Lecturers exhibit primarily delegating behaviour!
class LecturerWorkflow(ResponsibleAgentWorkflow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # There must be an attribute for every resource which can be effected as
        # the result of a Constraints.ResourceDelta being discharged.
        self.essays_written = 0
        self.working_programs = 0

    def register_acts(self):
        self.acts[self.write_essay] = {'essays_written': 1}
        self.acts[self.write_program] = {'working_programs': 1}


# TODO: Update with any student-specific actions.
# Students exhibit primarily discharging behaviour!
class StudentWorkflow(ResponsibleAgentWorkflow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # There must be an attribute for every resource which can be effected as
        # the result of a Constraints.ResourceDelta being discharged.
        self.essays_written = 0
        self.working_programs = 0

    def register_acts(self):
        self.acts[self.write_essay] = {'essays_written': 1}
        self.acts[self.write_program] = {'working_programs': 1}

class DummyWorkflow:
    is_workflow = True

treat_as_workflow(DummyWorkflow)
treat_as_workflow(StudentWorkflow)
treat_as_workflow(LecturerWorkflow)