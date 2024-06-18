from protean.reflection import declared_fields
from protean.utils import DomainObjects

from lending import Checkout


def test_checkout_entity_element_type():
    assert Checkout.element_type == DomainObjects.ENTITY


def test_checkout_entity_declared_fields():
    assert all(
        field_name in declared_fields(Checkout)
        for field_name in ["id", "book_id", "checked_out_at", "due_on"]
    )
