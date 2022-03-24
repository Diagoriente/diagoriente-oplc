from copy import copy
from dataclasses import dataclass
from contextlib import contextmanager
from oplc.model import DataSet, mk_data_set

from oplc.effect import pull_source, load_data_frame
from oplc.pipelines import (
        experiences_skills_data_source, jobs_skills_data_source, check_data
        )

import logging
logging.getLogger().setLevel(logging.INFO)

# The application state contains the information that either changes at runtime
# or is computed once at startup.

@dataclass(frozen=True)
class State:
    dataset: DataSet


# A state context manager allows to handle the state within a with statement:
#
# with state() as s: 
#    s.dataset = ...
#
# The global state is updated only when the context manager exits. This helps
# handling side effects cleanly, provided state changes in the with block are
# done immutably. The state bound in the with block is a shallow copy of the
# global state. When the block exits, the state is written back to the global 
# state. Within the block, the state members can be mutated multiple times and
# the global state update will be done atomically at the end, or not at all if
# an exception is raised. However, if nested values in the state object still
# reference the nested values of the global state. This means that any mutation
# applied to a nested value will mutate the global state. Care must be taken
# to avoid this in order to benefit from atomic state handling. Use
# dataclasses.replace to update objects immutably.

@contextmanager
def state():
    global app_state
    s = copy(app_state)
    yield s
    app_state = s


# At startup, the application pulls the data pieces from their respective
# sources.

experiences_skills_local_csv = pull_source(experiences_skills_data_source, "experiences_skills")
jobs_skills_local_csv = pull_source(jobs_skills_data_source, "jobs_skills")

# It then loads the data frames from the resulting local csvs

experiences_skills_df = load_data_frame(experiences_skills_local_csv)
jobs_skills_df = load_data_frame(jobs_skills_local_csv)

dataset = mk_data_set(
        experiences_skills=experiences_skills_df,
        jobs_skills=jobs_skills_df,
        )

# Some basic checks ensure that the data is valid
check_data(dataset)

# A global state stores all the data that will be needed at runtime beyond
# initialization. This is the global state that must be used within a with
# statement anywhere else to handle side effects cleanly. For example:
#
# from oplc.state import state
# with state as s:
#    s.dataset = ...

app_state = State(dataset=dataset)

