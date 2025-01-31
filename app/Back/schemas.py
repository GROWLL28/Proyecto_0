from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models import CategoriaEnum

class UsuarioBase(BaseModel):
    username: str

class UsuarioCreate(UsuarioBase):
    password: str

class Usuario(UsuarioBase):
    id: int
    imagen_perfil: Optional[str] = None

    class Config:
        orm_mode = True

class TareaBase(BaseModel):
    texto: str
    estado: Optional[str] = "Sin Empezar"
    categoria: Optional[CategoriaEnum] = CategoriaEnum.OTROS

class TareaCreate(TareaBase):
    pass

class Tarea(TareaBase):
    id: int
    fecha_creacion: datetime
    propietario_id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class MensajeRespuesta(BaseModel):
    message: str