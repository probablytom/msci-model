from queue import Queue, Empty
from threading import Event, RLock, Thread

from .task import Task
from .workflow import allocate_workflow_to, Idling

import inspect

class OutOfTurnsException(Exception):
    pass


class Actor(object):
    """
    Models the work behaviour of a self-directing entity.  Actors can be assigned tasks described by workflows which are
    executed in synchronization with actor's clock.
    """

    def __init__(self, logical_name, clock):
        self.logical_name = logical_name
        self.clock = clock

        self.tick_received = Event()
        self.tick_received.clear()
        self.waiting_for_tick = Event()
        self.waiting_for_tick.clear()

        self.busy = RLock()
        self.wait_for_directions = True
        self.thread = Thread(target=self.perform)

        self.clock.add_tick_listener(self)

        self._task_history = list()
        self.current_task = None

        self.task_queue = Queue()

        self.idling = Idling()
        allocate_workflow_to(self, self.idling, logging=False)

        self.next_turn = 0

    def allocate_task(self, workflow, entry_point, args=list()):

        entry_point_name = entry_point.func_name
        allocate_workflow_to(self, workflow)
        entry_point = workflow.__getattribute__(entry_point_name)

        allocated_task = Task(workflow, entry_point, args)
        self.task_queue.put(allocated_task)
        return allocated_task

    def log_task_initiation(self, workflow, entry_point, args):

        if self.current_task.initiated:
            self.current_task = self.current_task.append_sub_task(workflow, entry_point, args)

        self.current_task.initiate(self.clock.current_tick)

    def log_task_completion(self):
        self.current_task.complete(self.clock.current_tick)
        self.current_task = self.current_task.parent

    @property
    def task_history(self):
        return filter(lambda task: task.workflow.logging is not False, self._task_history)

    @property
    def last_completed_task(self):
        try:
            return self.task_history[-1]
        except IndexError:
            return None

    def task_count(self, task_func=None):

        def recursive_task_count(task_history):

            result = 0

            for completed_task in task_history:
                result += recursive_task_count(completed_task.sub_tasks)

                func = completed_task.entry_point.im_func if inspect.ismethod(completed_task.entry_point) \
                    else completed_task.entry_point

                if task_func is None or func.func_name == task_func.im_func.func_name:
                    result += 1

            return result

        return recursive_task_count(self.task_history)

    def perform(self):
        """
        Repeatedly polls the actor's asynchronous work queue until the actor is shutdown.  Tasks in the work queue are
        executed synchronously until shutdown.  On shutdown, all remaining tasks in the queue are processed before
        termination.  Task execution will halt immediately if the actor's clock runs up to it's maximum tick count.
        """
        while self.wait_for_directions or not self.task_queue.empty():
            try:
                try:
                    task = self.task_queue.get(block=False)
                except Empty:
                    task = Task(self.idling, self.idling.idle)

                if task is not None:
                    self._task_history.append(task)
                    self.current_task = task
                    task.entry_point(*task.args)

            except OutOfTurnsException:
                break

        # Ensure that clock can proceed for other listeners.
        self.clock.remove_tick_listener(self)
        self.waiting_for_tick.set()

    def start(self):
        self.thread.start()

    def shutdown(self):
        self.initiate_shutdown()
        self.wait_for_shutdown()

    def initiate_shutdown(self):
        self.wait_for_directions = False

    def wait_for_shutdown(self):
        self.thread.join()

    def incur_delay(self, delay):
        self.next_turn = max(self.next_turn, self.clock.current_tick)
        self.next_turn += delay

    def wait_for_turn(self):
        """
        A method that blocks while the actor's clock time is less than the time of the actor's next turn.
        """

        while self.clock.current_tick < self.next_turn:
            if self.clock.will_tick_again:
                self.waiting_for_tick.set()
                self.tick_received.wait()
                self.tick_received.clear()
            else:
                raise OutOfTurnsException()

    def notify_new_tick(self):
        self.waiting_for_tick.clear()
        self.tick_received.set()

    def __str__(self):
        return "a_%s" % self.logical_name

    def __repr__(self):
        return self.__str__()


class Team(object):
    """
    A collection of actors who synchronize their actions on a single clock.
    """

    def __init__(self, clock):
        self.clock = clock

        self.team_members = list()

    def add_member(self, logical_name):
        actor = Actor(logical_name, self.clock)
        self.team_members.append(actor)
        return actor

    def start(self):
        for actor in self.team_members:
            actor.start()

    @property
    def last_tick(self):

        def finish_ticks(developer):
            if developer.last_completed_task is None:
                return 0
            elif developer.last_completed_task.finish_tick is None:
                return self.clock.current_tick
            else:
                return developer.last_completed_task.finish_tick

        last_tick = reduce(max, map(finish_ticks, self.team_members))

        return last_tick

    def task_count(self, task):
        return sum(map(lambda actor: actor.task_count(task), self.team_members))
