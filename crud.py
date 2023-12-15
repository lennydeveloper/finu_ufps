from sqlalchemy.orm import Session
from sqlalchemy import func

# from models import User, Item
# from schemas import UserCreate, ItemCreate
# # from . import models, schemas

from models import Usuario, Estado, Facultad, Programa, GrupoInv, Convocatoria, Proyecto, Rol, Propuesta
from schemas import BaseUser, BaseConvocatoria
from fastapi import HTTPException

from src.utils.password_generator import get_encrypted_pass


def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()


def get_programas(db: Session, skip: int = 0, limit: int = 100):
    if limit == 0:
        return db.query(Programa).offset(skip).all()
    return db.query(Programa).offset(skip).limit(limit).all()


def get_facultades(db: Session, skip: int = 0, limit: int = 100):
    if limit == 0:
        return db.query(Facultad).offset(skip).all()
    return db.query(Facultad).offset(skip).limit(limit).all()


def get_grupos_inv(db: Session, skip: int = 0, limit: int = 100):
    if limit == 0:
        return db.query(GrupoInv).offset(skip).all()
    return db.query(GrupoInv).offset(skip).limit(limit).all()


def get_proyectos(db: Session, skip: int = 0, limit: int = 100):
    if limit == 0:
        return db.query(Proyecto).offset(skip).all()
    return db.query(Proyecto).offset(skip).limit(limit).all()


def get_usuarios(db: Session, skip: int = 0, limit: int = 100):
    if limit == 0:
        return db.query(Usuario).order_by(Usuario.id.asc()).offset(skip).all()
    return db.query(Usuario).order_by(Usuario.id.asc()).offset(skip).limit(limit).all()


def get_convocatorias(db: Session, skip: int = 0, limit: int = 100):
    if limit == 0:
        return db.query(Convocatoria).offset(skip).all()
    return db.query(Convocatoria).offset(skip).limit(limit).all()


def get_propuestas(db: Session, convocatoria_id: int = 0, usuario_id: int = 0, rol_id: int = 0):
    # Obtener propuestas para el rol de admin
    if rol_id == 1:
        return db.query(Propuesta).all()
    # Obtener propuestas (filtro por convocatoria)
    if convocatoria_id == 0:
        return db.query(Propuesta).filter(Propuesta.usuario_id == usuario_id).all()
    return db.query(Propuesta).filter(Propuesta.convocatoria_id == convocatoria_id).all()


def get_dashboard_totales(db: Session):
    convocatorias = db.query(Convocatoria).count()
    proyectos = db.query(Proyecto).count()
    presupuesto = db.query(func.sum(Proyecto.monto_financiado_finu)).scalar()
    docentes = db.query(Usuario).filter(Usuario.rol_id == 2).count()
    estudiantes = db.query(Usuario).filter(Usuario.rol_id == 3).count()
    grupos_inv = db.query(GrupoInv).count()

    return {
        'convocatorias': convocatorias,
        'proyectos': proyectos,
        'presupuesto': presupuesto,
        'docentes': docentes,
        'estudiantes': estudiantes,
        'grupos': grupos_inv
    }


def get_informacion_propuesta(db: Session):
    programas = db.query(Programa).all()
    grupos_inv = db.query(GrupoInv).all()
    facultades = db.query(Facultad).all()

    return {
        'programas': programas,
        'grupos_inv': grupos_inv,
        'facultades': facultades
    }


def create_user(db: Session, user: BaseUser):
    rol_db = db.query(Rol).filter(Rol.id == user.rol).first()
    programa_db = db.query(Programa).filter(Programa.id == user.programa).first()
    db_user = get_user_by_email(db, email=user.email)
    # avoid duplicate data
    if db_user:
        raise HTTPException(status_code=400, detail="Este email ya se encuentra registrado")
    # Check if rol exists
    if not rol_db:
        raise HTTPException(status_code=400, detail="El rol asignado a este usuario no se encuentra en la base de datos")
    # Check if programa exists
    if not programa_db:
        raise HTTPException(status_code=400, detail="El programa asignado a este usuario no se encuentra en la base de datos")

    hashed_password = get_encrypted_pass(user.clave)
    db_user = Usuario(
        nombres=user.nombres,
        apellidos=user.apellidos,
        telefono=user.telefono,
        email=user.email,
        clave=hashed_password,
        codigo=user.codigo,
        rol=rol_db,
        programa=programa_db
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def create_propuesta(db: Session, data: dict):
    # validación máximo 2 propuestas por usuario
    count_propuestas = db.query(Propuesta).filter(Propuesta.usuario_id == data['usuario_id']).count()
    if count_propuestas == 2:
        raise HTTPException(status_code=409, detail="La propuesta no pudo ser creada, ya tiene el máximo de propuestas permitidas para esta convocatoria")
    # get grupo_inv
    grupo_inv = db.query(GrupoInv).filter(GrupoInv.id == data['grupo_inv']).first()
    # Check if grupo_inv exists
    if not grupo_inv:
        raise HTTPException(status_code=400, detail="El grupo de inv. asignado a esta propuesta no se encuentra en la base de datos")

    # get programa
    programa = db.query(Programa).filter(Programa.id == data['programa']).first()
    # Check if programa exists
    if not programa:
        raise HTTPException(status_code=400, detail="El programa asignado a esta propuesta no se encuentra en la base de datos")

    # get facultad
    facultad = db.query(Facultad).filter(Facultad.id == data['facultad']).first()
    # Check if facultad exists
    if not facultad:
        raise HTTPException(status_code=400, detail="La facultad asignada a esta propuesta no se encuentra en la base de datos")
    # get user
    usuario = db.query(Usuario).filter(Usuario.id == data['usuario_id']).first()
    # Check if usuario exists
    if not usuario:
        raise HTTPException(status_code=400, detail="El usuario asignado a esta propuesta no se encuentra en la base de datos")

    # get estado
    estado = db.query(Estado).filter(Estado.id == 1).first()
    # Check if estado exists
    if not estado:
        raise HTTPException(status_code=400, detail="El estado asignado a esta propuesta no se encuentra en la base de datos")

    # get convocatoria
    convocatoria = db.query(Convocatoria).filter(Convocatoria.id == data['convocatoria_id']).first()
    # Check if convocatoria exists
    if not convocatoria:
        raise HTTPException(status_code=400, detail="La convocatoria asignada a esta propuesta no se encuentra en la base de datos")
    
    db_propuesta = Propuesta(
        nombre=data['titulo'],
        descripcion=data['descripcion'],
        grupos_investigacion=grupo_inv,
        usuario=usuario,
        estado=estado,
        facultad=facultad,
        programa=programa,
        convocatoria=convocatoria,
        url_archivo_propuesta=data['url_archivo_propuesta']
    )

    db.add(db_propuesta)
    db.commit()
    db.refresh(db_propuesta)

    return db_propuesta


# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(Item).offset(skip).limit(limit).all()


# def create_user_item(db: Session, item: ItemCreate, user_id: int):
#     db_item = Item(**item.model_dump(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item

# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(User).offset(skip).limit(limit).all()

# def get_user(db: Session, user_id: int):
#     return db.query(User).filter(User.id == user_id).first()