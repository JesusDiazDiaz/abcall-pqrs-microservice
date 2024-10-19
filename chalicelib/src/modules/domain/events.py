from dataclasses import dataclass

from chalicelib.src.seedwork.domain.event import DomainEvent


class IncidentEvent(DomainEvent):
    pass


@dataclass
class CreateIncident(IncidentEvent):
    pass
