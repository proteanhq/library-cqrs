from pytest_bdd import scenarios

from .step_defs.hold_steps import *  # noqa: F403

scenarios("./features")
