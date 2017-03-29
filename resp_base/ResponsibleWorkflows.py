from theatre_ag.theatre_ag.workflow import treat_as_workflow
from random import random, choice


class CourseworkWorkflow:

    def __init__(self):
        self.agent = None

    def assign_agent(self, agent):
        self.agent = agent

    # Lecturers can write essays
    # (We're calling papers essays, so as to simplify the model's ontology.)
    # RETURNS: tuple (a,b):
    #     a: success bool
    #     b: set of constraints with pass/failure
    def write_essay(self, agent):
        written_successfully = (random() > 0.1)
        written_successfully = True
        if written_successfully:
            if 'essays_written' not in agent.socio_states.keys():
                agent.socio_states['essays_written'] = 0
            agent.socio_states['essays_written'] += 1
            # Essay writing responsibilities have deadlines and essay details
            for i in range(len(agent.current_responsibility.importance_score_set.constraints)):
                agent.current_responsibility.importance_score_set.constraints[i].record_outcome(True)
        else:
            # Fail to write an essay one in ten times
            for i in range(len(agent.current_responsibility.importance_score_set.constraints)):
                agent.current_responsibility.importance_score_set.constraints[i].record_outcome(True)
            # One constraint will have failed.
            failed_responsibility = choice(
                range(len(agent.current_responsibility.importance_score_set.constraints)))
            agent.current_responsibility.importance_score_set.constraints[
                failed_responsibility].record_outcome(False)
        return (written_successfully, agent.current_responsibility.importance_score_set.constraints)

    def write_program(self, agent):
        written_successfully = (random() > 0.1)
        written_successfully = True
        if written_successfully:
            if 'working programs' not in agent.socio_states.keys():
                agent.socio_states['working_programs'] = 0
            agent.socio_states['working_programs'] += 1
            # Essay writing responsibilities have deadlines and essay details
            for i in range(len(agent.current_responsibility.importance_score_set.constraints)):
                agent.current_responsibility.importance_score_set.constraints[i].record_outcome(True)
        else:
            # Fail to write an essay one in ten times
            for i in range(len(agent.current_responsibility.importance_score_set.constraints)):
                agent.current_responsibility.importance_score_set.constraints[i].record_outcome(True)
                # One constraint will have failed.
            failed_responsibility = choice(
                range(len(agent.current_responsibility.importance_score_set.constraints)))
            agent.current_responsibility.importance_score_set.constraints[
                failed_responsibility].record_outcome(False)
        return (written_successfully, agent.current_responsibility.importance_score_set.constraints)


class DummyWorkflow:
    is_workflow = True

treat_as_workflow(CourseworkWorkflow)
