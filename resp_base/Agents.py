from theatre_ag.theatre_ag.actor import Actor as TheatreActor
from theatre_ag.theatre_ag import default_cost
from theatre_ag.theatre_ag.task import Task
from .Responsibilities import Responsibility, ImportanceScoreSet, Obligation
from abc import ABCMeta
from .utility_functions import mean, flatten
from .Responsibilities import Act, ResponsibilityEffect
from copy import copy



class ResponsibleAgent(TheatreActor):
    responsible = True  # This will be a toggle for deactivating the formalism

    __metaclass__ = ABCMeta

    def __init__(self, notions, name, clock,  workflows: list):
        super().__init__(name, clock)
        self.responsibilities = copy(notions)  # Default beliefs about the world
        self.notions = copy(notions)
        self.consequential_responsibilities = []  # All discharged constraints
        self.workflows = workflows
        self.idle_act = Act(self.idling.idle, self.idling)

        # Assign all of the workflows to me
        [workflow.assign_agent(self) for workflow in self.workflows]

        # To be updated with the responsibility the current action represents
        self.current_responsibility = None

        # An act is a bound method. self.acts is a dictionary of the form:
        #   {effect: (act_entry_point, workflow, args)}
        # ..where the effect is a list of tuples, where each tuple is a string and an integer effect on the atttribute
        #     the string represents.
        self.acts = {}

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
        intended_effect = [effect for effect in intended_effect
                           if 'duration' not in effect]
        return self.acts.get(intended_effect,
                             self.idle_act)

    @property
    def actionable_responsibilities(self):
        return [resp for resp in copy(self.responsibilities)
                if resp not in self.notions]

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
            return max(resps,
                       key=lambda x: mean(x.importance_score_set.importances))

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

        # Depending on whether the next action is to idle or is a free
        # action, act accordingly.
        if next_action is not self.idle_act:
            # Add its duration
            raise NotImplemented  # I need to change the costing function to Tim's new method!
            duration = \
                self.current_responsibility.calculate_effect()['duration']
            next_action = default_cost(duration)(next_action)

        else:
            # We're idling
            workflow = self.idling

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

    def register_act(self,
                     effect: ResponsibilityEffect,
                     act: Act):
        self.acts[effect] = act

    def register_new_workflow(self,
                              workflow):
        workflow.assign_agent(self)
        self.workflows.append(workflow)
