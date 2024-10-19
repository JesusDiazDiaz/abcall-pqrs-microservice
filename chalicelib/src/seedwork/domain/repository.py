from abc import ABC, abstractmethod
from uuid import UUID


class Repository(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def add(self, entity):
        pass

    @abstractmethod
    def get(self, id: UUID):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def remove(self, entity):
        pass

    @abstractmethod
    def update(self, id, entity):
        pass



class Mapper(ABC):
    @abstractmethod
    def get_type(self) -> type:
        pass

    @abstractmethod
    def entity_to_dto(self, entity):
        pass

    @abstractmethod
    def dto_to_entity(self, dto: any):
        pass
