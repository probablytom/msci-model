from theatre_ag.theatre_ag.actor import Actor as TheatreActor
from theatre_ag.theatre_ag.task import Task
from .Constraints import Deadline, ResourceDelta
from .Responsibilities import Responsibility, Obligation
from abc import ABCMeta
from .utility_functions import mean, flatten
from .Responsibilities import Act, ResponsibilityEffect
from copy import copy, deepcopy
from time import sleep


class BasicResponsibleAgent(TheatreActor):
    responsible = True  # This will be a toggle for deactivating the formalism

    __metaclass__ = ABCMeta

    def __init__(self,
                 notions,
                 name,
                 clock,
                 workflows: list,
                 sociotechnical_states = {},
                 interpreting_coefficients = {}):
        super().__init__(name, clock)

        self.interpreting_coefficients = interpreting_coefficients

        # Make a responsibility for self for chilling out, which idling fulfils
        chill_deadline = Deadline(1, clock)
        chill_effect = ResourceDelta({'personal_enjoyment': 1})
        chill = Obligation([chill_deadline,
                            chill_effect])
        chill.set_importances([0.2, 0.2])
        chill_resp = Responsibility(chill, self, self)
        notions.append(self.interpret(chill_resp))

        self.responsibilities = copy(notions)  # Default beliefs about the world
        self.notions = copy(notions)
        self.consequential_responsibilities = []  # All discharged constraints
        self.workflows = workflows
        self.socio_states = sociotechnical_states
        self.idle_act = Act(ResponsibilityEffect({'personal_enjoyment': 1}),
                            self.idling.idle,
                            self.idling)

        # Assign all of the workflows to me
        for workflow in self.workflows:
            workflow.assign_agent(self)

        # To be updated with the responsibility the current action represents
        self.current_responsibility = None

        # An act is a bound method. self.acts is a dictionary of the form:
        #   {effect: (act_entry_point, workflow, args)}
        # ..where the effect is a list of tuples, where each tuple is a string and an integer effect on the atttribute
        #     the string represents.
        self.acts = {}

    def delegate_responsibility(self,
                                obligation: Obligation,
                                importances: list,
                                delegee):  # Make this a ResponsibleAgent
        obligation.set_importances(importances)
        resp = Responsibility(obligation, self, delegee)
        accepted = resp.delegee.accept_responsibility(resp)
        if not accepted:
            raise NotImplemented("What happens if a responsibility \
                                  isn't allocated?")

    def interpret(self,
                  resp: Responsibility):
        resp = copy(resp)
        for factor, coefficient in self.interpreting_coefficients.items():
            for constraint in resp.constraints:
                if factor in constraint.factors.keys() or factor == constraint.__class__:

                    # Work out the new importance value.
                    old_importance = constraint.importance
                    new_importance = old_importance * coefficient
                    new_importance = max(min(1, new_importance), 0)  # Normalise!
                    constraint.assign_importance(new_importance)

        # Return the responsibility with a new set of constraints
        return resp

    def __decide_acceptance(self, resp):
        # importances = [constraint.importance
        #                for constraint in resp.constraints]
        # return mean(importances) > 0.5
        return True

    def accept_responsibility(self, resp: Responsibility):
        interpreted_responsibility = self.interpret(resp)
        accepted = self.__decide_acceptance(interpreted_responsibility)
        if accepted:
            self.responsibilities.append(interpreted_responsibility)
        return accepted

    def judge_degree_responsible(self,
                                 other_agent):

        # Get a new list of responsibilities, with importance scores
        # re-interpreted by this agent's perspective on responsibility.
        def re_interpret(resp: Responsibility):
            resp = deepcopy(resp)
            def restore_original_importance(resp):
                for constraint in resp.constraints:
                    constraint.reset_importance(constraint.original_importance)

            restore_original_importance(resp)
            return self.interpret(resp)
        newly_interpreted_resps = [re_interpret(resp)
                                   for resp in other_agent.responsibilities]

        # ...is the below still accurate?
        # TODO: review.
        # With these newly interpreted responsibilities, for type of responsibility,
        # calculate the average of the sum of the constraints of that type multiplied by their success as a boolean.
        #               -------        ---        ------------------------                     --------------------
        #                  ^            ^                     ^                                        ^- failure counts as 0
        #                  |            |                     |-- The responsibility will have many constraints -- calculate each factor seperately.
        #                  |            |-- Because there's potentially multiple constraints with the same factors, we want to sum the scores of each separate factor.
        #                  |-- Because there's potentially multiple constraints of the same factor, we want to weight the successes by the failures -- so, calculate the mean of all of the factors' summed scores.
        #
        degree_responsible = {}
        constraints = [constraint
                       for responsibility in newly_interpreted_resps
                       for constraint in responsibility.constraints]
        for constraint in constraints:
            for factor in constraint.factors.keys():
                if factor not in degree_responsible.keys():
                    degree_responsible[factor] = (0, 0)
                score, count = degree_responsible[factor]
                count += 1
                if constraint.outcome:
                    score += constraint.importance

        for factor, scores in degree_responsible.items():
            score, count = scores
            degree_responsible[factor] = score/count  # calculate the average

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
        intended_effect.disregard('duration')
        return self.acts.get(intended_effect,
                             self.idle_act)

    @property
    def actionable_responsibilities(self):
        return self.responsibilities ## To be changed by actors who dont act on all notions

    def choose_responsibility(self):
        '''
        Choose a responsibility with the highest average importance across various
        factors.
        TODO: make this smarter! Just taking the mean doesn't take into account
            the nature of the importances.
        TODO: Consider deadlines! Implement an eisenhower matrix, to weigh
            importance against urgency?
        '''
        resps = self.actionable_responsibilities
        if resps == []:
            return None
        else:
            resp = max(resps,
                       key=lambda x: sum(x.importances))
            # print([(resp.calculate_effect(), resp.importances) for resp in self.responsibilities])
            return resp

    def next_action(self):
        resp_chosen = self.choose_responsibility()
        if resp_chosen is not None:
            self.current_responsibility = resp_chosen
            discharge_act = self.choose_action(resp_chosen)
        else:
            discharge_act = self.idle_act

        return discharge_act

    def get_next_task(self):
        # Get the next action
        next_action = self.next_action()

        # Create and return the relevant task
        return Task(next_action.entry_point_function,
                    next_action.workflow,
                    next_action.args)

    def calculate_delay(self, entry_point, workflow=None, args=()):
        # If the current responsibility is None, we're idling.
        if self.current_responsibility is None:
            return 1  # Duration of an idle
        else:
            # Get the duration of the current responsibility as the length of the task.
            return self.current_responsibility.calculate_effect().get('duration')

    def handle_task_return(self, task, value):
        if value is not None:
            discharged_successfully, constraint_satisfactions = value
            self.consequential_responsibilities.append(constraint_satisfactions)
            if discharged_successfully:
                if self.current_responsibility not in self.notions:
                    self.responsibilities.remove(self.current_responsibility)
                self.current_responsibility = None

    def register_act(self,
                     act: Act):
        act.args = [self]
        act.entry_point_function.default_cost = 0
        self.acts[act.effect] = act

    def register_new_workflow(self,
                              workflow):
        workflow.assign_agent(self)
        self.workflows.append(workflow)

    def get_sociotechnical_state(self, state_key):
        return self.socio_states.get(state_key,
                                     None)


class LazyAgent(BasicResponsibleAgent):
    def __init__(self,
                 notions,
                 name,
                 clock,
                 workflows: list,
                 sociotechnical_states = {},
                 interpreting_coefficients = {Deadline: 0.5}):
        super().__init__(notions,
                         name,
                         clock,
                         workflows,
                         copy(sociotechnical_states),
                         copy(interpreting_coefficients))


class HedonisticAgent(BasicResponsibleAgent):
    def __init__(self,
                 notions,
                 name,
                 clock,
                 workflows: list,
                 sociotechnical_states = {},
                 interpreting_coefficients = {'personal_enjoyment': 5}):
        super().__init__(notions,
                         name,
                         clock,
                         workflows,
                         copy(sociotechnical_states),
                         copy(interpreting_coefficients))

    def handle_task_return(self, task, value):
        if value is not None:
            discharged_successfully, constraint_satisfactions = value
            self.consequential_responsibilities.append(constraint_satisfactions)
            if discharged_successfully:
                if self.current_responsibility not in self.notions:
                    self.responsibilities.remove(self.current_responsibility)
                self.current_responsibility = None


class StudiousAgent(BasicResponsibleAgent):
    def __init__(self,
                 notions,
                 name,
                 clock,
                 workflows: list,
                 sociotechnical_states = {},
                 interpreting_coefficients = {'working_programs': 2,
                                              'essays_written': 2}):
        super().__init__(notions,
                         name,
                         clock,
                         workflows,
                         copy(sociotechnical_states),
                         copy(interpreting_coefficients))
