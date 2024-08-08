from pytest_bdd import scenarios

from .step_defs.addition_steps import *  # noqa: F403

scenarios("./features")
