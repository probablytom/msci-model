from abc import ABCMeta
from theatre_ag import SynchronizingClock


class AbstractConstraint:

    __metaclass__ = ABCMeta

    def __init__(self, factors: dict):
        self.factors = factors

    def assign_importance(self, importance):
        self.importance = importance


class Deadline(AbstractConstraint):

    def __init__(self,
                 duration: int,
                 timeline: SynchronizingClock):
        super().__init__({})  # Deadlines have only one factor, which is special
        self.time_created = timeline.current_tick  # This needs to be changed to time assigned
        self.timeline = timeline

    # TODO: REMOVE THIS IN FAVOUR OF AGENT_BASED EVALUATION
    def evaluate(self):
        return self.factors['length'] < \
            (self.timeline.current_tick - self.time_created)


class ResourceDelta(AbstractConstraint):
    pass
