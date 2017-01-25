'''

    The universe that actors reside within, so that satisfaction criteria can
     ...be specified and agreed on by all actors.

'''

from abc import ABCMeta


class RougeActorException:
    pass


class Universe:
    __metaclass__ = ABCMeta

    tick = 0
    actors_in_tick = []
    actors = []

    def collect_tick(actor):
        if actor in Universe.actors_in_tick:
            Universe.actors_in_tick.remove(actor)
            if Universe.actors_in_tick == []:
                Universe.__release_new_tick()
        else:
            raise RougeActorException("Actor: " + actor +
                                      " trying to act twice in one tick!")

    def __release_new_tick():
        Universe.tick += 1
        Universe.actors_in_tick = Universe.actors
        for actor in Universe.actors_in_tick:
            actor.__act_in_tick()

    # TODO: Spawn a clock for the actor with synchronised ticks
    # TODO: Handle race conditions with this and a new tick rolling over
    def birth_actor(new_actor):
        Universe.actors.append(new_actor)
