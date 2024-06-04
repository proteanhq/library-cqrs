from pytest_bdd import scenarios

from .step_defs.place_a_hold_on_a_book_steps import *  # noqa: F403

scenarios("./features/place_a_hold_on_a_book.feature")
