from protean import BaseEvent
from protean.fields import Boolean, DateTime, Float, Identifier, String, Text


class BookInstanceAdded(BaseEvent):
    instance_id = Identifier(required=True)
    isbn = String(required=True)
    title = String(required=True)
    summary = Text(required=True)
    price = Float(required=True)
    is_circulating = Boolean(required=True)
    added_at = DateTime(required=True)
