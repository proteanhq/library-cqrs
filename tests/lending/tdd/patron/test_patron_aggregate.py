"""This test file contains tests for the `Patron` aggregate

Patron Aggregate Structure:
- Patron ID - Identifier
- Type (Regular or Researcher) - String
- Holds - HasMany
- Checkouts - HasMany
"""

from protean.reflection import declared_fields
from protean.utils import DomainObjects

from lending import Patron


def test_patron_aggregate_element_type():
    assert Patron.element_type == DomainObjects.AGGREGATE


def test_patron_aggregate_has_defined_fields():
    assert all(
        field_name in declared_fields(Patron)
        for field_name in ["id", "patron_type", "holds", "checkouts"]
    )


def test_patron_factory_model_fixture(active_patron):
    assert active_patron is not None
    assert len(active_patron.holds) == 2
    assert len(active_patron.checkouts) == 2