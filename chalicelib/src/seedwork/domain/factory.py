from abc import abstractmethod, ABC
from .repository import Mapper


class Factory(ABC):
    @abstractmethod
    def create_object(self, obj: any, mapper: Mapper=None):
        ...