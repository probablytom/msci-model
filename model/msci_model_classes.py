'''

    Classes to be used in the msci model

'''

from structures import Authority, ResponsibleActor
from structures import Obligation


class Lecturer(Authority):

    def contruct_obligation(self, action) -> Obligation:
        # TODO: change nominal 0.75 to something more reasonable.
        return Obligation(action, self, 0.75)

    def delegate(self, obligation: Obligation, enactor: Actor) -> None:
        acceptance = enactor.recieve_obligation(obligation)
        if not acceptance:
            pass


class Student(ResponsibleActor):

    def recieve_obligation(obligation: Obligation) -> bool:
        lecturer_obligation = isinstance(obligation.authority, Lecturer)
        if lecturer_obligation:
            self.assigned_responsibilities.append(obligation)  # Where's timestamp coded into the obligation? How can we check against how long has passed?
        return lecturer_obligation

    def interpret_score(self, obligation):
        return obligation.score * 0.75
