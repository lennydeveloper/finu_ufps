from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from datetime import date, datetime

from database import Base


# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)

#     items = relationship("Item", back_populates="owner")


# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))

#     owner = relationship("User", back_populates="items")

class Facultad(Base):
    __tablename__ = "facultades"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)

    programas = relationship("Programa", back_populates="facultades")
    directores_facultad = relationship("DirFacultad", back_populates="facultades")


class Programa(Base):
    __tablename__ = "programas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    facultad_id = Column(Integer, ForeignKey("facultades.id"), nullable=True)

    facultades = relationship("Facultad", back_populates="programas")
    directores_programa = relationship('DirPrograma', back_populates="programas")


class GrupoInv(Base):
    __tablename__ = "grupos_inv"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)

    directores_grupos_inv = relationship('DirGrupoInv', back_populates="grupos_inv")


class DirFacultad(Base):
    __tablename__ = "dir_facultad"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    facultad_id = Column(Integer, ForeignKey("facultades.id"))

    facultades = relationship("Facultad", back_populates="directores_facultad")


class DirGrupoInv(Base):
    __tablename__ = "dir_grupo_inv"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    grupo_inv_id = Column(Integer, ForeignKey("grupos_inv.id"))

    grupos_inv = relationship('GrupoInv', back_populates="directores_grupos_inv")


class DirPrograma(Base):
    __tablename__ = "dir_programa"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    programa = Column(Integer, ForeignKey("programas.id"))

    programas = relationship('Programa', back_populates="directores_programa")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String)
    apellidos = Column(String)
    telefono = Column(String)
    email = Column(String, index=True)
    clave = Column(String)


class Convocatoria(Base):
    __tablename__ = "convocatorias"

    id = Column(Integer, primary_key=True, index=True)
    fecha_inscripcion = Column(Date)
    fecha_evaluacion = Column(Date)
    fecha_publicacion_resultados = Column(Date)
    # id_coordinador (FK pending)
    titulo_convocatoria = Column(String, index=True)
    descripcion_convocatoria = Column(String)
    anio_convocatoria = Column(Date)


class Proyecto(Base):
    __tablename__ = "proyectos"    

    id = Column(Integer, primary_key=True, index=True)
    contrato = Column(String, nullable=True)
    anio = Column(String, nullable=True)
    convocatoria = Column(String, nullable=True)
    proyecto = Column(String, nullable=True)
    tipo_proyecto = Column(String, nullable=True)
    alianza = Column(String, nullable=True)
    investigador = Column(String, nullable=True)
    tipo_investigador = Column(String, nullable=True)
    dedicacion_horas = Column(String, nullable=True)
    grupo_investigacion = Column(String, nullable=True)
    facultad = Column(String) # revisar F, nullable=TrueK
    departamento = Column(String) # revisar F, nullable=TrueK
    celular = Column(String, nullable=True)
    supervisado = Column(String, nullable=True)
    monto_financiado_finu = Column(String, nullable=True)
    duracion = Column(String, nullable=True)
    prorroga_1 = Column(String, nullable=True)
    prorroga_2 = Column(String, nullable=True)
    fecha_inicio_contrato = Column(String, nullable=True)
    fecha_terminacion_contrato = Column(String, nullable=True)
    informes_parciales_entregados = Column(String, nullable=True)
    informe_final = Column(String, nullable=True)
    presupuesto = Column(String, nullable=True)
    presupuesto_no_aprobado = Column(String, nullable=True)
    evaluador = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)
    producto = Column(String, nullable=True)
    nombre_producto = Column(String, nullable=True)
