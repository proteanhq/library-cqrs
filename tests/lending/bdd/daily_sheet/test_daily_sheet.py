from pytest_bdd import scenarios

from .step_defs.daily_sheet_steps import *  # noqa: F403

scenarios("./features")
