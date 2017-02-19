import theatre_ag
from utility_functions import flatten
from random import random


class NotImplementedException(Exception):
    pass


class Obligation:
    def __init__(self, constraint_set):
        self.constraint_set = constraint_set


class Responsibility:
    def __init__(self, obligation, importance_score_set, authority, delegee):
        self.obligation = obligation
        self.importance_score_set = importance_score_set
        self.authority = authority
        self.delegee = delegee


class Constraint:
    def __init__(self, constraint_type, constraint_text):
        self.constraint_type = constraint_type
        self.constraint_text = constraint_text

    def assign_importance(self, importance):
        self.importance = importance

    def record_outcome(self, outcome):
        self.outcome = outcome


# What are the differences between a theatre actor and a resp. actor?
class ResponsibleAgent(theatre_ag.Actor):

    def __init__(self, notions, *args, **kwargs):
        super(self, *args, **kwargs)
        self.responsibilities = notions  # Default beliefs about the world
        self.consequential_responsibilities = []  # All discharged constraints

        # To be updated with the responsibility the current action represents
        self.current_responsibility = None

    def allocate_responsibility(self, resp):
        accepted = resp.delegee.allocate_responsibility(resp)
        if not accepted:
            raise NotImplementedException("What happens if a responsibility \
                                          isn't allocated?")

    def interpret(self, resp):
        return resp

    def accept_responsibility(self, resp):
        accepted = self.interpret(resp)
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

    # Worth noting: when an action's chosen, it needs to be put into a workflow
    #     -> we need to keep track of *why* we're performing that action!
    #     -> we need to know what responsibility we're discharging
    # RETURNS: a function which returns a tuple (a,b):
    #     a: the success or failure of the discharge
    #     b: the set of constraint satisfactions (the consequential
    #       responsibility)
    def choose_action(self, responsibility):
        raise NotImplementedException("Return a function to be run to fulfil \
                                      a responsibility")

    # Selects a responsibility to discharge, attempts to discharge it, and
    # modifies the list of responsibilities accordingly.
    def discharge(self):
        resp_chosen = self.choose_responsibility()
        discharge_function = self.choose_action(resp_chosen)
        discharged_successfully, constraint_satisfactions = discharge_function()
        self.consequential_responsibilities.append(constraint_satisfactions)
        if discharged_successfully:
            self.responsibilities.remove(resp_chosen)


# TODO: Update with any lecturer-specific actions.
# Lecturers exhibit primarily delegating behaviour!
class Lecturer(ResponsibleAgent):

    # TODO: Do lecturers need to do this, given they don't discharge?
    #     (An action of theirs might be delegation?)
    def choose_action(self, responsibility):
        pass

    # TODO: Modify this for judging student responsibility?
#     def judge_degree_responsible(self, other_agent):

    # TODO: Decide whether to implement, given a lecturer doesn't discharge
    # responsibility.
    def allocate_responsibility(self, resp):
        pass

    # TODO: Decide whether to implement, given a lecturer doesn't discharge
    # responsibility.
    def interpret(self, resp):
        pass


# TODO: Update with any student-specific actions.
# Students exhibit primarily discharging behaviour!
class Student(ResponsibleAgent):

    def __init__(self, *args, **kwargs):
        super.__init__(self, *args, **kwargs)

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
    def write_essay(self):
        if random() > 0.1:
            self.essays_written += 1
        else:
