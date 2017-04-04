from theatre_ag.theatre_ag.actor import Actor as TheatreActor
from theatre_ag.theatre_ag.task import Task
from .Constraints import Deadline, ResourceDelta
from .Responsibilities import Responsibility, Obligation
from abc import ABCMeta
from .utility_functions import mean, flatten
from .Responsibilities import Act, ResponsibilityEffect
from .ResponsibleWorkflows import CourseworkWorkflow, IncompetentCourseworkWorkflow
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
                            chill_effect],
                            name="idle")
        chill.set_importances([0.25, 0.5])
        self.chill_resp = Responsibility(chill, self, self)
        notions.append(self.interpret(self.chill_resp))

        self.responsibilities = copy(notions)  # Default beliefs about the world
        self.notions = copy(notions)
        self.consequential_responsibilities = []  # All discharged constraints
        self.workflows = workflows
        self.socio_states = sociotechnical_states
        self.idle_act = Act(ResponsibilityEffect({'personal_enjoyment': 1}),
                            self.idling.idle,
                            self.idling)
        self.basic_judgement_responsible = 0.25  # How responsible is someone if you don't know what they've done before?

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
        resp = Responsibility(copy(obligation), self, delegee)
        accepted = resp.delegee.accept_responsibility(resp)
        if not accepted:
            raise NotImplemented("What happens if a responsibility \
                                  isn't allocated?")

    def interpret(self,
                  resp: Responsibility):
        resp = copy(resp)
        for factor, coefficient in self.interpreting_coefficients.items():
            for constraint_index in range(len(resp.constraints)):
                old_constraint = resp.constraints[constraint_index]
                constraint = copy(old_constraint)
                importance = constraint.importance

                # Work out the new importance value, if there is one.
                if factor in constraint.factors.keys() or factor == constraint.__class__:
                    # constraint.interpreted = False
                    importance = importance * coefficient
                    importance = max(min(1, importance), 0)  # Normalise!

                constraint.assign_importance(importance)
                resp.constraints[constraint_index] = constraint

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

    def __judge_degree_responsible(self, other_agent):
        # Re-interpret constraints
        resps = [r
                 for r in copy([c[0] for c in other_agent.consequential_responsibilities])]
        resps += [r
                  for r in other_agent.responsibilities
                  if r not in other_agent.notions]
        temp = [r
                  for r in other_agent.responsibilities
                  if r not in other_agent.notions]

        for responsibility in resps:
            for i in range(len(responsibility.constraints)):
                constraint = copy(responsibility.constraints[i])
                constraint.importance = constraint.original_importance
                responsibility.constraints[i] = self.interpret(constraint)

        # Calculate each resource type's specific responsibility
        specific_responsibilities = {}
        importance = 0
        outcome = False
        def process_factor(factor, outcome, importance):
            if factor not in specific_responsibilities.keys():
                specific_responsibilities[factor] = (0, 0)
            score, count = specific_responsibilities[factor]
            count += 1
            if outcome is None:
                outcome = False
            if outcome:
                score += importance
            specific_responsibilities[factor] = (score, count)

        for responsibility in resps:
            for constraint in responsibility.constraints:
                importance = constraint.importance
                outcome = constraint.outcome
                if type(constraint) == Deadline:
                    process_factor(Deadline, outcome, importance)
                for factor in constraint.factors.keys():
                    process_factor(factor, outcome, importance)

        for factor, score_tuple in specific_responsibilities.items():
            specific_responsibilities[factor] = score_tuple[0]/score_tuple[1]

        return specific_responsibilities

    def basic_responsibility_judgement(self):
        return self.basic_judgement_responsible

    def general_responsibility_judgement(self, other_agent):
        judgement = self.__judge_degree_responsible(other_agent)
        return mean(judgement.values())

    def specific_responsibility_judgement(self, other_agent, resource_type):
        return self.__judge_degree_responsible(other_agent).get(resource_type,
                                                                self.basic_judgement_responsible)

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
            resp = sorted(resps,
                                key=lambda x: sum(x.importances))[::-1][0]
            self.TEMP=sorted(resps,
                                key=lambda x: sum(x.importances))[::-1]
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
            consequential_responsibility = copy(self.current_responsibility)
            consequential_responsibility.obligation.constraint_set = [copy(c) for c in constraint_satisfactions]
            self.consequential_responsibilities.append((consequential_responsibility, discharged_successfully))
            if discharged_successfully or True:
                self.responsibilities.pop(self.responsibilities.index(self.current_responsibility))
                temp = self.current_responsibility in self.responsibilities
                self.current_responsibility = None
        else:
            if not self.current_responsibility == self.chill_resp:
                self.responsibilities.pop(self.responsibilities.index(self.current_responsibility))
            consequential_responsibility = copy(self.current_responsibility)
            self.consequential_responsibilities.append((consequential_responsibility, True))
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


class StudiousAgent(BasicResponsibleAgent):
    def __init__(self,
                 notions,
                 name,
                 clock,
                 workflows: list,
                 sociotechnical_states = {},
                 interpreting_coefficients = {'working_programs': 5,
                                              'essays_written': 5}):
        super().__init__(notions,
                         name,
                         clock,
                         workflows,
                         copy(sociotechnical_states),
                         copy(interpreting_coefficients))


class Lecturer(BasicResponsibleAgent):
    def __init__(self,
                 notions,
                 name,
                 clock,
                 workflows: list,
                 sociotechnical_states = {},
                 interpreting_coefficients = {}):
        super().__init__(notions,
                         name,
                         clock,
                         workflows,
                         copy(sociotechnical_states),
                         copy(interpreting_coefficients))
