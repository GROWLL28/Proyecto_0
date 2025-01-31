from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

class CategoriaEnum(str, enum.Enum):
    HOGAR = "Hogar"
    TRABAJO = "Trabajo"
    URGENTE = "Urgente"
    PERSONAL = "Personal"
    OTROS = "Otros"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    imagen_perfil = Column(String, nullable=True)

    tareas = relationship("Tarea", back_populates="propietario", cascade="all, delete-orphan")

class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    texto = Column(String, index=True)
    estado = Column(String, default="Sin Empezar")
    categoria = Column(Enum(CategoriaEnum), default=CategoriaEnum.OTROS)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    propietario_id = Column(Integer, ForeignKey("usuarios.id"))

    propietario = relationship("Usuario", back_populates="tareas")