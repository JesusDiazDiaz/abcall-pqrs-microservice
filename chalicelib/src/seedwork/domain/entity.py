import uuid
from dataclasses import dataclass, field
from datetime import datetime

from .exceptions import ImmutableIdException
from .rules import EntityIdIsImmutable


@dataclass
class Entity:
    """Entity base class.

    Attributes:
        id: Unique identifier of the entity.

    See Also:
        - https://enterprisecraftsmanship.com/posts/entity-base-class/

    """

    id: uuid.UUID = field(hash=True)
    _id: uuid.UUID = field(init=False, repr=False, hash=True)
    created_at: datetime = field(default=datetime.now())
    updated_at: datetime = field(default=datetime.now())

    @classmethod
    def next_id(cls) -> uuid.UUID:
        return uuid.uuid4()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: uuid.UUID) -> None:
        if not EntityIdIsImmutable(self).is_valid():
            raise ImmutableIdException()
        self._id = self.next_id()