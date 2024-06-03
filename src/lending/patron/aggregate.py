from enum import Enum

from ..domain import lending


class PatronType(Enum):
    REGULAR = "REGULAR"
    RESEARCHER = "RESEARCHER"


@lending.aggregate
class Patron:
    """This is the Patron Aggregate."""
    pass
