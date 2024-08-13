from protean.utils import DomainObjects
from protean.utils.reflection import declared_fields

from lending import Hold


def test_hold_entity_element_type():
    assert Hold.element_type == DomainObjects.ENTITY


def test_hold_entity_declared_fields():
    assert all(
        field_name in declared_fields(Hold)
        for field_name in ["id", "book_id", "hold_type"]
    )
