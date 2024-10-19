from chalicelib.src.seedwork.domain.exceptions import FactoryException


class ImplementationNotExistsForFactoryException(FactoryException):
    def __init__(self, message='No implementation exists for the repository with the given type.'):
        self.__message = message

    def __str__(self):
        return str(self.__message)