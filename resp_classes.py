import theatre_ag


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


# What are the differences between a theatre actor and a resp. actor?
class Agent(theatre_ag.Actor):

    def __init__(self, notions, *args, **kwargs):
        super(*args, **kwargs)
        self.responsibilities = notions  # Default beliefs about the world
        self.current_responsibility = None  # To be updated with the responsibility the current action represents

    def allocate_responsibility(self, resp):
        accepted = resp.delegee.allocate_responsibility(resp)
        if not accepted:
            raise NotImplementedException("What happens if a responsibility \
                                          isn't allocated?")

    def interpret(self, resp):
        raise NotImplementedException("Implement an interpreting function")

    def accept_responsibility(self, resp):
        accepted = self.interpret(resp)
        if accepted:
            self.responsibilities.append(resp)
        return accepted

    def judge_degree_responsible(other_agent):
        raise NotImplementedException("Implement this part of the formalism!")

    # Worth noting: when an action's chosen, it needs to be put into a workflow
    #     -> we need to keep track of *why* we're performing that action!
    #     -> we need to know what responsibility we're discharging
    # TODO: choose next action, update self.current_responsibility, act,
    #   mark responsibility discharged
    def choose_action(self):
        raise NotImplementedException("Return a function to be run to fulfil \
                                      a responsibility")
