from typing import Union
from pydantic import BaseModel
from datetime import date
from models import Rol


class UserLoginSchema(BaseModel):
    email: str
    clave: str

    class Config:
        orm_mode = True


class RolSchema(BaseModel):
    id: int
    nombre: str

    class Config:
        orm_mode = True


class BaseUser(BaseModel):
    nombres: str
    apellidos: str
    telefono: str
    email: str
    clave: str


class CreateUserSchema(BaseUser):
    rol: int
    codigo: str
    programa: int

    class Config:
        orm_mode = True


class UserSchema(BaseUser):
    rol_id: int

    class Config:
        orm_mode = True


class BaseConvocatoria(BaseModel):
    titulo: str
    descripcion: str
    fecha_inicio: date
    fecha_limite: date
    fecha_inicio_evaluacion: date
    fecha_fin_evaluacion: date
    fecha_publicacion_resultados: date
    tipo_convocatoria: str


class ConvocatoriaSchema(BaseConvocatoria):
    id: int
    anio_convocatoria: str
    url_archivo: str

    class Config:
        orm_mode = True


class FinuBase(BaseModel):
    nombre: str


class FacultadSchema(FinuBase):
    id: int

    class Config:
        orm_mode = True


class ProgramaSchema(FinuBase):
    id: int
    facultad: Union[FacultadSchema, None] = None

    class Config:
        orm_mode = True


class UserResponseSchema(BaseUser):
    id: int
    rol: RolSchema
    programa: ProgramaSchema

    class Config:
        orm_mode = True


class EstadoSchema(BaseModel):
    id: int
    nombre: str
    descripcion: str

    class Config:
        orm_mode = True


class GrupoInvSchema(FinuBase):
    id: int

    class Config:
        orm_mode = True


class BasePropuestaSchema(BaseModel):
    id: int
    nombre: str
    descripcion: str
    grupos_investigacion: GrupoInvSchema
    programa: ProgramaSchema
    convocatoria: ConvocatoriaSchema
    facultad: FacultadSchema
    estado: EstadoSchema
    usuario: UserResponseSchema
    url_archivo_propuesta: str
    observaciones: Union[str, None] = None
    calificacion: Union[int, None] = None
    url_archivo_calificacion: Union[str, None] = None

    class Config:
        orm_mode = True


class BaseProyectoSchema(BaseModel):
    tipo_proyecto: str
    departamento: str
    fecha_terminacion_contrato: str
    estado: str
    alianza: str
    celular: str
    informes_parciales_entregados: str
    observaciones: str
    id: int
    investigador: str
    supervisado: str
    informe_final: str
    producto: str
    tipo_investigador: str
    monto_financiado_finu: str
    presupuesto: str
    nombre_producto: str
    contrato: str
    dedicacion_horas: str
    duracion: str
    presupuesto_no_aprobado: str
    propuesta_id: BasePropuestaSchema
    anio: str
    grupo_investigacion: str
    prorroga_1: str
    convocatoria: str
    facultad: str
    prorroga_2: str
    evaluador: str
    proyecto: str
    fecha_inicio_contrato: str

    class Config:
        orm_mode = True


class ProyectoResponseSchema(BaseModel):
    proyectos: BaseProyectoSchema
    total_proyectos: int

    class Config:
        orm_mode = True

# class ItemBase(BaseModel):
#     title: str
#     description: Union[str, None] = None


# class ItemCreate(ItemBase):
#     pass


# class Item(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         orm_mode = True


# class UserBase(BaseModel):
#     email: str


# class UserCreate(UserBase):
#     password: str


# class User(UserBase):
#     id: int
#     is_active: bool
#     items: list[Item] = []

#     class Config:
#         orm_mode = True
