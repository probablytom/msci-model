from theatre_ag.theatre_ag.workflow import treat_as_workflow
from .Constraints import Deadline
from random import random, choice


class CourseworkWorkflow:

    def __init__(self):
        self.agent = None
        self.competence = {'essays_written': 0.95,
                           'working_programs': 0.95}

    def assign_agent(self, agent):
        self.agent = agent

    # Lecturers can write essays
    # (We're calling papers essays, so as to simplify the model's ontology.)
    # RETURNS: tuple (a,b):
    #     a: success bool
    #     b: set of constraints with pass/failure
    def write_essay(self, agent):
        written_successfully = (random() < self.competence['essays_written'])
        if 'essays_written' not in agent.socio_states.keys():
            agent.socio_states['essays_written'] = 0
        for i in range(len(agent.current_responsibility.constraints)):
            agent.current_responsibility.constraints[i].record_outcome(True)
        if written_successfully:
            agent.socio_states['essays_written'] += 1
        else:
            choice([c for c in agent.current_responsibility.constraints if type(c) is not Deadline]).record_outcome(False)
        return (written_successfully, agent.current_responsibility.constraints)

    def write_program(self, agent):
        written_successfully = (random() < self.competence['working_programs'])
        if 'working_programs' not in agent.socio_states.keys():
            agent.socio_states['working_programs'] = 0
        for i in range(len(agent.current_responsibility.constraints)):
            agent.current_responsibility.constraints[i].record_outcome(True)
        if written_successfully:
            agent.socio_states['working_programs'] += 1
        else:
            choice([c for c in agent.current_responsibility.constraints if type(c) is not Deadline]).record_outcome(False)
        return (written_successfully, agent.current_responsibility.constraints)


class IncompetentCourseworkWorkflow(CourseworkWorkflow):
    def __init__(self):
        super().__init__()
        self.competence = {'essays_written': 0.2,
                           'working_programs': 0.2}


class DummyWorkflow:
    is_workflow = True

treat_as_workflow(CourseworkWorkflow)
