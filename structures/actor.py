import abc
from structures import Obligation


#  TODO: Should this be swapped out for Tim's theatre_ag?
#        Not sure whether ticks help or complicate.
# An ABC for a regular ol' agent
class Actor:
    __metaclass__ = abc.ABCMeta
    agent_count = 0

    def __init__(self):
        self.actor_count = Actor.agent_count
        Actor.actor_count += 1


class Authority(Actor):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super.__init__()

    @abc.abstractmethod
    def construct_obligation(self, action) -> Obligation:
        '''A function which creates an obligation out of an action to be done'''
        return

    @abc.abstractmethod
    def delegate(self, obligation: Obligation, enactor: Actor) -> None:
        '''A function which assigns an obligation to a given actor'''
        return


# An ABC for defining a responsible agent class
class ResponsibleActor(Actor):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super.__init__()
        self.assigned_responsibilities = []

    @abc.abstractmethod
    def recieve_obligation(obligation: Obligation) -> bool:
        '''A function which listens to an obligations from some authority.
        Accepts an Obligation to be assessed by the agent for acceptance
        Returns bool indicating whether obligation was accepted by the actor'''

    @abc.abstractmethod
    def interpret_score(self, obligation):
        '''Used to determine percieved scores of an assigned responsibility.'''
        return
