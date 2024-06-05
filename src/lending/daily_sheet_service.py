from datetime import datetime

from lending import Patron, Book, HoldStatus
from lending.domain import lending


@lending.domain_service(part_of=[Patron, Book])
class DailySheetService:
    def __init__(self, patrons: list[Patron]):
        self.patrons = patrons

    def run(self):
        self._expire_holds()

    def _expire_holds(self):
        for patron in self.patrons:
            for hold in patron.holds:
                if (
                    hold.status == HoldStatus.ACTIVE.value
                    and hold.expiry_date < datetime.now()
                ):
                    patron.expire_hold(hold.id)
