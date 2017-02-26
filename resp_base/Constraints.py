from abc import ABCMeta, abstractmethod
from theatre_ag import SynchronizingClock


class AbstractConstraint:

    __metaclass__ = ABCMeta

    def __init__(self, factors: dict):
        self.factors = factors

    def assign_importance(self, importance):
        self.importance = importance


class Deadline(AbstractConstraint):

    def __init__(self,
                 factors: dict,
                 timeline: SynchronizingClock):
        super().__init__(factors)
        self.time_created = timeline.current_tick
        self.timeline = timeline

    # TODO: REMOVE THIS IN FAVOUR OF AGENT_BASED EVALUATION
    def evaluate(self):
        return self.factors['length'] < \
            (self.timeline.current_tick - self.time_created)


class ResourceDelta(AbstractConstraint): pass
