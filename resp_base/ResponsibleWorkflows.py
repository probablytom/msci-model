from theatre_ag.theatre_ag.workflow import treat_as_workflow
from random import random, choice


class CourseworkWorkflow:

    def __init__(self):
        self.agent = None
        self.competence = {'essays_written': 0.9,
                           'working_programs': 0.9}

    def assign_agent(self, agent):
        self.agent = agent

    # Lecturers can write essays
    # (We're calling papers essays, so as to simplify the model's ontology.)
    # RETURNS: tuple (a,b):
    #     a: success bool
    #     b: set of constraints with pass/failure
    def write_essay(self, agent):
        written_successfully = (random() < self.competence['essays_written'])
        written_successfully = True
        if written_successfully:
            if 'essays_written' not in agent.socio_states.keys():
                agent.socio_states['essays_written'] = 0
            agent.socio_states['essays_written'] += 1
            # Essay writing responsibilities have deadlines and essay details
            for i in range(len(agent.current_responsibility.constraints)):
                agent.current_responsibility.constraints[i].record_outcome(True)
        else:
            # Fail to write an essay one in ten times
            for i in range(len(agent.current_responsibility.constraints)):
                agent.current_responsibility.constraints[i].record_outcome(True)
                # One constraint will have failed.
            failed_responsibility = choice(
                range(len(agent.current_responsibility.constraints)))
            agent.current_responsibility.constraints[
                failed_responsibility].record_outcome(False)
        return (written_successfully, agent.current_responsibility.constraints)

    def write_program(self, agent):
        written_successfully = (random() < self.competence['working_programs'])
        written_successfully = True
        if written_successfully:
            if 'working programs' not in agent.socio_states.keys():
                agent.socio_states['working_programs'] = 0
            agent.socio_states['working_programs'] += 1
            # programming responsibilities have deadlines and specs
            for i in range(len(agent.current_responsibility.constraints)):
                agent.current_responsibility.constraints[i].record_outcome(True)
        else:
            # Fail to write an essay one in ten times
            for i in range(len(agent.current_responsibility.constraints)):
                agent.current_responsibility.constraints[i].record_outcome(True)
                # One constraint will have failed.
            failed_responsibility = choice(
                range(len(agent.current_responsibility.constraints)))
            agent.current_responsibility.constraints[
                failed_responsibility].record_outcome(False)
        return (written_successfully, agent.current_responsibility.constraints)


class IncompetentCourseworkWorkflow(CourseworkWorkflow):
    def __init__(self):
        super().__init__()
        self.competence = {'essays_written': 0.4,
                           'working_programs': 0.4}


class DummyWorkflow:
    is_workflow = True

treat_as_workflow(CourseworkWorkflow)
