from pytest_bdd import scenarios

from .step_defs.checkout_steps import *  # noqa: F403

scenarios("../../../features/checkouts")
