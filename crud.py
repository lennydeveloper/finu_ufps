from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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


def get_propuestas(db: Session, convocatoria_id: int = 0, usuario_id: int = 0):
    print(convocatoria_id)
    if convocatoria_id == 0:
        return db.query(Propuesta).filter(Propuesta.usuario_id == usuario_id).all()
    return db.query(Propuesta).filter(Propuesta.convocatoria_id == convocatoria_id).all()


def get_dashboard_totales(db: Session):
    convocatorias = db.query(Convocatoria).count()
    proyectos = db.query(Proyecto).count()
    presupuesto = 0
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
    # get grupo_inv
    grupo_inv = db.query(GrupoInv).filter(GrupoInv.id == data['grupo_inv']).first()
    # get programa
    programa = db.query(Programa).filter(Programa.id == data['programa']).first()
    # get facultad
    facultad = db.query(Facultad).filter(Facultad.id == data['facultad']).first()
    # get user
    usuario = db.query(Usuario).filter(Usuario.id == data['usuario_id']).first()
    # get estado
    estado = db.query(Estado).filter(Estado.id == 1).first()
    # get convocatoria
    convocatoria = db.query(Convocatoria).filter(Convocatoria.id == data['convocatoria_id']).first()
   
    # Check if grupo_inv exists
    if not grupo_inv:
        raise HTTPException(status_code=400, detail="El grupo de inv. asignado a esta propuesta no se encuentra en la base de datos")
    
    # Check if programa exists
    if not programa:
        raise HTTPException(status_code=400, detail="El programa asignado a esta propuesta no se encuentra en la base de datos")
    
    # Check if facultad exists
    if not facultad:
        raise HTTPException(status_code=400, detail="La facultad asignada a esta propuesta no se encuentra en la base de datos")
    
    # Check if usuario exists
    if not usuario:
        raise HTTPException(status_code=400, detail="El usuario asignado a esta propuesta no se encuentra en la base de datos")

    # Check if estado exists
    if not estado:
        raise HTTPException(status_code=400, detail="El estado asignado a esta propuesta no se encuentra en la base de datos")

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
        url_archivo=data['url_archivo']
    )

    db.add(db_propuesta)
    db.commit()
    db.refresh(db_propuesta)

    return db_propuesta


def create_convocatoria(db: Session, convocatoria: BaseConvocatoria):
    db_convocatoria = Convocatoria(
        titulo=convocatoria.titulo,
        descripcion=convocatoria.descripcion,
        fecha_inicio=convocatoria.fecha_inicio,
        fecha_limite=convocatoria.fecha_limite,
        fecha_inicio_evaluacion=convocatoria.fecha_inicio_evaluacion,
        fecha_fin_evaluacion=convocatoria.fecha_fin_evaluacion,
        fecha_publicacion_resultados=convocatoria.fecha_publicacion_resultados,
    )
    db.add(db_convocatoria)
    db.commit()
    db.refresh(db_convocatoria)

    return db_convocatoria


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