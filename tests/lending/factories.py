import factory

from datetime import datetime, timedelta


from lending import Patron, PatronType, Hold, HoldType, HoldStatus, Checkout


class HoldFactory(factory.Factory):
    class Meta:
        model = Hold
    
    book_instance_id = factory.Faker('uuid4')
    hold_type = HoldType.OPEN_ENDED.value
    status = HoldStatus.ACTIVE.value
    request_date = factory.Faker('date_time')
    expiry_date = factory.Faker('date_time')


class CheckoutFactory(factory.Factory):
    class Meta:
        model = Checkout

    book_instance_id = factory.Faker('uuid4')
    checkout_date = factory.LazyFunction(datetime.now)
    due_date = factory.LazyFunction(lambda: datetime.now() + timedelta(days=7))


class NamedHolds(factory.ListFactory):
    class Meta:
        model = Hold

class NamedCheckouts(factory.ListFactory):
    class Meta:
        model = Checkout

class PatronFactory(factory.Factory):
    class Meta:
        model = Patron

    patron_type = PatronType.REGULAR.value
    holds = factory.List([
        factory.SubFactory(
            HoldFactory,
            patron_id=factory.SelfAttribute('..patron_id'),
        ) for _ in range(2)
    ], list_factory=NamedHolds)
    checkouts = factory.List([
        factory.SubFactory(CheckoutFactory) for _ in range(2)
    ], list_factory=NamedCheckouts)