import theatre_ag
from abc import abstractmethod, ABCMeta
from .utility_functions import flatten, mean
from .Constraints import Deadline, ResourceDelta
from random import random, choice


class Obligation:
    def __init__(self, constraint_set: list):
        self.constraint_set = constraint_set


# An importance score set is deliberately seperate from the responsibility,
# becase we allocate new importances to constraints every time we assign an
# obligation.
class ImportanceScoreSet:
    def __init__(self,
                 obligation: Obligation,
                 importances: list):
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

        return ResponsibilityEffect(total_effect)


class ResponsibilityEffect:
    def __init__(self, effect_dict):
        self.effects = [(k, v) for k, v in effect_dict.items()]

    def __hash__(self):
        return str(self).__hash__()  # Hacky but should work...

    @property
    def effect_dict(self):
        return dict(self.effects)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.effect_dict == other.effect_dict

    def get(self, effect_key):
        if effect_key in self.effect_dict.keys():
            return self.effect_dict[effect_key]
        return 0  # No effect for a key which this repsonsibility doesn't effect!

    def disregard(self, effect_key):
        '''
        Alters the ResponsibilityEffect so as to ignore certain parameters.
        This method mutates the ResponsibilityEffect, so it's best to make a backup.
        :param effect_key: The key that should be ignored in this ResponsibilityEffect
        '''
        self.effects = [item for item in self.effects
                        if effect_key not in item]

    def __str__(self):
        return "ResponsibilityEffect: " + str(self.effect_dict)


class Act:
    def __init__(self, effect, entry_point_function, workflow=None, args=()):
        self.entry_point_function = entry_point_function
        self.workflow = workflow
        self.args = args
        self.effect = effect