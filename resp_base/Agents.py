from theatre_ag.theatre_ag.actor import Actor as TheatreActor
from .ResponsibleWorkflows import ResponsibleAgentWorkflow


class ResponsibleAgent(TheatreActor):
    def __init__(self, workflow: ResponsibleAgentWorkflow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workflow = workflow
        self.workflow.agent = self

    def delegate_responsibility(self, *args, **kwargs):
        return self.workflow.delegate_responsibility(*args, **kwargs)

    def accept_responsibility(self, *args, **kwargs):
        return self.workflow.accept_responsibility(*args, **kwargs)

    def handle_return_value(self, *args, **kwargs):
        return self.workflow.handle_return_value(*args, **kwargs)

    def get_next_task(self, *args, **kwargs):
        result = self.workflow.get_next_task()
        #if self.logical_name == 'student_0':
        #    print (result)

        return result

    def handle_return_value(self, *args, **kwargs):
        return self.workflow.handle_return_value(*args, **kwargs)

class Student(ResponsibleAgent):
    @property
    def essays_written(self, *args, **kwargs):
        return self.workflow.essays_written

    @property
    def working_programs(self, *args, **kwargs):
        return self.workflow.working_programs

class Lecturer(ResponsibleAgent):
    @property
    def essays_written(self, *args, **kwargs):
        return self.workflow.essays_written

    @property
    def working_programs(self, *args, **kwargs):
        return self.workflow.working_programs

