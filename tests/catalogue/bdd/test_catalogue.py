from pytest_bdd import scenarios

from .step_defs.catalogue_steps import *  # noqa: F403

scenarios("./features")
