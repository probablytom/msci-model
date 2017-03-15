from theatre_ag import Actor as TheatreActor
from theatre_ag.workflow import Idling as TheatreIdling
from theatre_ag import default_cost
from theatre_ag.task import Task
from theatre_ag.actor import OutOfTurnsException
from .Responsibilities import Responsibility
from abc import ABCMeta, abstractmethod
from .utility_functions import mean, flatten, sign
from random import random, choice
from copy import copy


class NotImplementedException(Exception):
    pass


class ResponsibleAgent(TheatreActor):

    responsible = True  # This will be a toggle for deactivating the formalism

    __metaclass__ = ABCMeta

    def __init__(self, notions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.responsibilities = notions  # Default beliefs about the world
        self.notions = notions
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

    def allocate_responsibility(self, resp):
        accepted = resp.delegee.allocate_responsibility(resp)
        if not accepted:
            raise NotImplementedException("What happens if a responsibility \
                                          isn't allocated?")

    def interpret(self, resp):
        return resp

    def accept_responsibility(self, resp: Responsibility):
        resp = self.interpret(resp)
        # TODO: fix this calculation
        accepted = mean(resp.importance_score_set.values()) > 0.5
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

    # RETURNS: a function which returns a tuple (a,b):
    #     a: the success or failure of the discharge
    #     b: the set of constraint satisfactions (the consequential
    #       responsibility)
    # Will choose the first action which seems to move resources in the intended
    # direction.
    def choose_action(self, responsibility):
        intended_effect = responsibility.calculate_effect()
        effect_signs = dict(zip(intended_effect.keys(),
                            [sign(value)
                             for value in intended_effect.values()]
                            ))
        for act, act_effect_signs in self.acts_effect_signs.items():
            if effect_signs == act_effect_signs:
                return act
        raise NotImplementedException("If no action can successfully \
                                      discharge the responsibility, what do \
                                      we do?")

    # Choose a responsibility with the highest average importance across various
    # factors.
    # TODO: make this smarter! Just taking the mean doesn't take into account
    #     the nature of the importances.
    # TODO: Consider deadlines! Implement an eisenhower matrix, to weigh
    #     importance against urgency?
    def choose_responsibility(self):
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
            discharge_function = self.choose_action(resp_chosen)
        else:
            discharge_function = self.idling.idle
        return discharge_function

    @abstractmethod
    def register_acts(self):
        pass

    # TODO: Add responsibilities to the task queue?
    def perform(self):
        while self.wait_for_directions or self.responsibilities == self.notions:
            try:
                next_action = self.next_action()
                if next_action != self.idling.idle:
                    duration = \
                        self.current_responsibility.calculate_effect()['duration']
                    task_function = default_cost(next_action, duration)

                # TODO: Do we actually need to provide a workflow class here?
                task = Task(None, task_function)

                self._task_history.append(task)
                self.current_task = task
                task.entry_point(*task.args)

            except OutOfTurnsException:
                break

        # Ensure that clock can proceed for other listeners.
        self.clock.remove_tick_listener(self)
        self.waiting_for_tick.set()


# TODO: Update with any lecturer-specific actions.
# Lecturers exhibit primarily delegating behaviour!
class Lecturer(ResponsibleAgent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # There must be an attribute for every resource which can be effected as
        # the result of a Constraints.ResourceDelta being discharged.
        self.essays_written = 0

    # TODO: Do lecturers need to do this, given they don't discharge?
    #     (An action of theirs might be delegation?)
    def choose_action(self, responsibility):
        pass

    # TODO: Modify this for judging student responsibility?
    # def judge_degree_responsible(self, other_agent):

    # TODO: Decide whether to implement, given a lecturer doesn't discharge
    # responsibility.
    def allocate_responsibility(self, resp):
        pass

    # TODO: Decide whether to implement, given a lecturer doesn't discharge
    # responsibility.
    def interpret(self, resp):
        pass

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

    def register_acts(self):
        self.acts[self.write_essay] = {'essays_written': 1}


# TODO: Update with any student-specific actions.
# Students exhibit primarily discharging behaviour!
class Student(ResponsibleAgent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # There must be an attribute for every resource which can be effected as
        # the result of a Constraints.ResourceDelta being discharged.
        self.essays_written = 0

    # TODO: How do students decide what they'll do next?
    def choose_action(self, responsibility):
        pass

    # TODO:
    def allocate_responsibility(self, resp):
        pass

    # TODO:
    def interpret(self, resp):
        pass

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

    def register_acts(self):
        self.acts[self.write_essay] = {'essays_written': 1}


class Idling(TheatreIdling):
    # TODO: make this default to
    pass
