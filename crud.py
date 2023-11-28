from sqlalchemy.orm import Session

# from models import User, Item
# from schemas import UserCreate, ItemCreate
# # from . import models, schemas

from models import Usuario, Facultad, Programa, GrupoInv
from schemas import BaseUser
from fastapi import HTTPException

from src.utils.password_generator import get_encrypted_pass


def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()


def get_programas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Programa).offset(skip).limit(limit).all()


def get_facultades(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Facultad).offset(skip).limit(limit).all()


def get_grupos_inv(db: Session, skip: int = 0, limit: int = 100):
    return db.query(GrupoInv).offset(skip).limit(limit).all()


def create_user(db: Session, user: BaseUser):
    db_user = get_user_by_email(db, email=user.email)
    # avoid duplicate data
    if db_user:
        raise HTTPException(status_code=400, detail="Este email ya se encuentra registrado")

    hashed_password = get_encrypted_pass(user.clave)
    db_user = Usuario(nombres=user.nombres, apellidos=user.apellidos, telefono=user.telefono, email=user.email, clave=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


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