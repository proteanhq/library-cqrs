from protean.reflection import declared_fields
from protean.utils import DomainObjects

from lending import Checkout


def test_checkout_entity_element_type():
    assert Checkout.element_type == DomainObjects.ENTITY


def test_checkout_entity_declared_fields():
    assert all(
        field_name in declared_fields(Checkout)
        for field_name in ["id", "book_instance_id", "checkout_date", "due_date"]
    )


def test_checkout_factory_model_fixture(checkout):
    assert checkout is not None
