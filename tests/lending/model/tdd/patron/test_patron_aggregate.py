"""This test file contains tests for the `Patron` aggregate

Patron Aggregate Structure:
- Patron ID - Identifier
- Type (Regular or Researcher) - String
- Holds - HasMany
- Checkouts - HasMany
"""

from protean.utils import DomainObjects
from protean.utils.reflection import declared_fields

from lending import Patron


def test_patron_aggregate_element_type():
    assert Patron.element_type == DomainObjects.AGGREGATE


def test_patron_aggregate_has_defined_fields():
    assert all(
        field_name in declared_fields(Patron)
        for field_name in ["id", "patron_type", "holds", "checkouts"]
    )
