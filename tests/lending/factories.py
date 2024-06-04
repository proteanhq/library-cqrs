import factory
from uuid import uuid4

from datetime import datetime, timedelta


from lending import (
    Patron,
    PatronType,
    Hold,
    HoldType,
    HoldStatus,
    Checkout,
    Book,
    BookInstance,
    BookInstanceStatus,
    BookInstanceType,
)


class HoldFactory(factory.Factory):
    class Meta:
        model = Hold

    id = factory.LazyAttribute(lambda o: uuid4())
    book_instance_id = factory.Faker("uuid4")
    hold_type = HoldType.OPEN_ENDED.value
    status = HoldStatus.ACTIVE.value
    request_date = factory.Faker("date_time")
    expiry_date = factory.Faker("date_time")


class CheckoutFactory(factory.Factory):
    class Meta:
        model = Checkout

    book_instance_id = factory.Faker("uuid4")
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


class ActivePatronFactory(factory.Factory):
    class Meta:
        model = Patron
    
    
    @factory.post_generation
    def holds(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.holds = extracted
        else:
            self.holds = [HoldFactory(patron=self) for _ in range(2)]

    @factory.post_generation
    def checkouts(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.checkouts = extracted
        else:
            self.checkouts = [CheckoutFactory() for _ in range(2)]


class NamedBookInstances(factory.ListFactory):
    class Meta:
        model = BookInstance


class BookInstanceFactory(factory.Factory):
    class Meta:
        model = BookInstance

    book_instance_type = BookInstanceType.CIRCULATING.value
    status = BookInstanceStatus.AVAILABLE.value


class BookFactory(factory.Factory):
    class Meta:
        model = Book

    isbn = factory.Faker("isbn13")
    title = factory.Faker("sentence")
    price = factory.Faker("pyfloat", left_digits=2, right_digits=2)
    book_instances = factory.List(
        [
            factory.SubFactory(
                BookInstanceFactory,
                book_id=factory.SelfAttribute("..book_id"),
            )
            for _ in range(2)
        ],
        list_factory=NamedBookInstances,
    )
