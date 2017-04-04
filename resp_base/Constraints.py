from abc import ABCMeta
from theatre_ag.theatre_ag import SynchronizingClock


class ImproperImportanceResetError(Exception):
    pass


class AbstractConstraint:

    __metaclass__ = ABCMeta

    def __init__(self, factors: dict):
        self.factors = factors
        self.outcome = None
        self.interpreted = False
        self.original_importance = None
        self.importance = None

    def assign_importance(self, importance):
        self.original_importance = self.importance
        self.importance = importance
        # Only assign if we haven't already.
        if self.original_importance is None:
            self.original_importance = importance  # If this is the first assignment, keep track of the true original importance
        self.interpreted = True

    def reset_importance(self, new_score=None):
        self.importance = self.original_importance
        self.original_importance = None
        self.interpreted = False
        if new_score is not None:
            self.assign_importance(new_score)

    def record_outcome(self, outcome):
        self.outcome = outcome


class Deadline(AbstractConstraint):

    def __init__(self,
                 duration: int,
                 timeline: SynchronizingClock):
        super().__init__({})  # Deadlines have only one factor, which is special
        # This needs to be changed to time assigned
        self.time_created = timeline.current_tick
        self.timeline = timeline
        self.duration = duration

    # TODO: REMOVE THIS IN FAVOUR OF AGENT-BASED EVALUATION
    def evaluate(self):
        return self.factors['length'] < \
            (self.timeline.current_tick - self.time_created)


class ResourceDelta(AbstractConstraint):
    pass
