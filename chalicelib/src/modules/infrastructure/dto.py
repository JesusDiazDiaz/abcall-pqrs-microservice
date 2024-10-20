import enum
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum, Date, Text


Base = declarative_base()


class IncidentType(enum.Enum):
    PETICION = "Peticion"
    QUEJA = "Queja"
    RECLAMO = "Reclamo"


class CommunicationType(enum.Enum):
    EMAIL = "Email"
    TELEFONO = "Telefono"
    SMS = "Sms"
    CHAT = "Chat"


class Status(enum.Enum):
    ABIERTO = "Abierto"
    CERRADO = "Cerrado"


class Incidence(Base):
    __tablename__ = 'incidences'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(Status), nullable=False)
    date = Column(Date, nullable=False)
    estimated_close_date = Column(Date, nullable=True)
    user_sub = Column(String, nullable=False)
    type = Column(Enum(IncidentType), nullable=False)
    communication_type = Column(Enum(CommunicationType), nullable=False)


class IncidenceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Incidence
        load_instance = True
