'''

    Actionables, like obligations and responsibilities.

'''
# TODO: Actually write this


class Obligation:
    def __init__(self, action, authority, score):
        self.action = action
        self.authority = authority
        self.score = score


class Responsibility:
    def __init__(self, obligation: Obligation):
        self.action = obligation.action
        self.authority = obligation.authority
        self.score = obligation.score
