from theatre_ag.theatre_ag.workflow import treat_as_workflow
from random import random, choice


class CourseworkWorkflow:

    def __init__(self):
        self.essays_written = 0
        self.working_programs = 0
        self.agent = None

    def assign_agent(self, agent):
        self.agent = agent

    # Lecturers can write essays
    # (We're calling papers essays, so as to simplify the model's ontology.)
    # RETURNS: tuple (a,b):
    #     a: success bool
    #     b: set of constraints with pass/failure
    @default_cost(1)
    def write_essay(self):
        written_successfully = (random() > 0.1)
        if written_successfully:
            self.essays_written += 1
            # Essay writing responsibilities have deadlines and essay details
            for i in range(len(self.agent.curent_responsibility.importance_score_set.constraints)):
                self.agent.curent_responsibility.importance_score_set.constraints[i].record_outcome(True)
        else:
            # Fail to write an essay one in ten times
            for i in range(len(self.agent.curent_responsibility.importance_score_set.constraints)):
                self.agent.curent_responsibility.importance_score_set.constraints[i].record_outcome(True)
            # One constraint will have failed.
            failed_responsibility = choice(
                range(len(self.agent.curent_responsibility.importance_score_set.constraints)))
            self.agent.curent_responsibility.importance_score_set.constraints[
                failed_responsibility].record_outcome(False)
        return (written_successfully, self.agent.curent_responsibility.importance_score_set.constraints)

    @default_cost(1)
    def write_program(self):
        written_successfully = (random() > 0.1)
        if written_successfully:
            self.working_programs += 1
            # Essay writing responsibilities have deadlines and essay details
            for i in range(len(self.agent.curent_responsibility.importance_score_set.constraints)):
                self.agent.curent_responsibility.importance_score_set.constraints[i].record_outcome(True)
        else:
            # Fail to write an essay one in ten times
            for i in range(len(self.agent.curent_responsibility.importance_score_set.constraints)):
                self.agent.curent_responsibility.importance_score_set.constraints[i].record_outcome(True)
                # One constraint will have failed.
            failed_responsibility = choice(
                range(len(self.agent.curent_responsibility.importance_score_set.constraints)))
            self.agent.curent_responsibility.importance_score_set.constraints[
                failed_responsibility].record_outcome(False)


class DummyWorkflow:
    is_workflow = True

treat_as_workflow(CourseworkWorkflow)
