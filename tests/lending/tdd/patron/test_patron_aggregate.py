"""This test file contains tests for the `Patron` aggregate

Patron Aggregate Structure:
- Patron ID - Identifier
- Type (Regular or Researcher) - String
- Holds - HasMany
- Checkouts - HasMany
"""

import pytest

from protean.utils import DomainObjects

from lending import Patron


def test_patron_aggregate_properties():
    assert Patron.element_type == DomainObjects.AGGREGATE
