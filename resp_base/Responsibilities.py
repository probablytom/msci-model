from .Constraints import Deadline, ResourceDelta
from random import random


class UnbalancedImportancesError(Exception):
    pass


class Obligation:
    def __init__(self,
                 constraint_set: list,
                 name="unnamed_responsibility"):
        self.constraint_set = constraint_set
        self.name = name

    def set_importances(self, importances):
        if len(importances) != len(self.constraint_set):
            raise UnbalancedImportancesError()
        for i in range(len(importances)):
            self.constraint_set[i].assign_importance(importances[i])


class Responsibility:
    def __init__(self,
                 obligation: Obligation,
                 authority,
                 delegee,
                 id=None):
        if id is None:
            self.id = random() * 100000000
        else:
            self.id = id
        self.obligation = obligation
        self.authority = authority
        self.delegee = delegee

    @property
    def constraints(self):
        return self.obligation.constraint_set

    @property
    def importances(self):
        return [constraint.importance
                for constraint in self.constraints]

    def original_importances(self):
        return [constraint.original_importance
                for constraint in self.constraints]

    def calculate_effect(self):
        '''
        Calculates the desired effect of a responsibility.
        :return: A ResponsibilityEffect, which accounts for all effects of this responsibility's constraints.
        '''
        total_effect = {'duration': 0}
        for constraint in self.constraints:
            if isinstance(constraint, ResourceDelta):
                for factor, effect in constraint.factors.items():
                    if factor not in total_effect.keys():
                        total_effect[factor] = 0
                    total_effect[factor] += effect
            elif isinstance(constraint, Deadline):
                total_effect['duration'] += constraint.duration

        return ResponsibilityEffect(total_effect)

    def __eq__(self, other):
        return self.id == other.id

    @property
    def name(self):
        return self.obligation.name


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