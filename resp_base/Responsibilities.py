import theatre_ag
from abc import abstractmethod, ABCMeta
from .utility_functions import flatten, mean
from .Constraints import Deadline, ResourceDelta
from random import random, choice


class Obligation:
    def __init__(self, constraint_set):
        self.constraint_set = constraint_set


# An importance score set is deliberately seperate from the responsibility,
# becase we allocate new importances to constraints every time we assign an
# obligation.
class ImportanceScoreSet:
    def __init__(self, obligation, importances):
        constraints = obligation.constraint_set
        if len(constraints) != len(importances):
            class MissingImportanceInformationException(Exception): pass
            raise MissingImportanceInformationException()
        self.constraints = constraints
        self.importances = importances
        self.importance_map = dict(zip(constraints, importances))


class Responsibility:
    def __init__(self, importance_score_set, authority, delegee):
        self.importance_score_set = importance_score_set
        self.constraints = importance_score_set.constraints
        self.authority = authority
        self.delegee = delegee

    def calculate_effect(self):
        total_effect = {'duration': 0}
        for constraint in self.importance_score_set.constraints:
            if isinstance(constraint, ResourceDelta):
                for factor, effect in constraint.factors.items():
                    if factor not in total_effect.keys():
                        total_effect[factor] = 0
                    total_effect[factor] += effect
            elif isinstance(constraint, Deadline):
                total_effect['duration'] += constraint.duration

        return total_effect
