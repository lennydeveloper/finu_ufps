from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from crud import get_user_by_email, create_user # , get_users, get_user, create_user_item, get_items
from models import Base, Usuario
from schemas import UserLoginSchema, UserSchema, BaseUser # , ItemCreate, Item, User, UserCreate
from database import SessionLocal, engine

# utils >>>
from src.utils.password_generator import get_encrypted_pass, decode_password
from src.utils.excel_to_database import get_projects_from_excel
from src.utils.get_raw_data import obtener_facultades, obtener_grupos_inv, obtener_programas_academicos

Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def home(db: Session = Depends(get_db)):
    projects = get_projects_from_excel()
    try:
        db.bulk_save_objects(projects, update_changed_only=False)
        db.commit()
        content = jsonable_encoder({ "success": "La información ha sido agregada exitosamente." })
        return JSONResponse(content=content, status_code=200)
    except Exception as e:
        print(e)
        content = jsonable_encoder(content = { "error": "La información de los proyectos no pudo ser cargada." })
        return JSONResponse(content=content, status_code=500)
    

@app.get('/upload/facultades')
def cargar_facultades(db: Session = Depends(get_db)):
    facultades = obtener_facultades()
    try:
        db.bulk_save_objects(facultades, update_changed_only=False)
        db.commit()
        content = jsonable_encoder({ "success": "Las facultades han sido agregadas exitosamente." })
        return JSONResponse(content=content, status_code=200)
    except Exception as e:
        print(e)
        content = jsonable_encoder(content = { "error": "La información de las facultades no pudo ser cargada." })
        return JSONResponse(content=content, status_code=500)
    

@app.get('/upload/grupos-investigacion')
def cargar_grupos_inv(db: Session = Depends(get_db)):
    grupos_inv = obtener_grupos_inv()
    try:
        db.bulk_save_objects(grupos_inv, update_changed_only=False)
        db.commit()
        content = jsonable_encoder({ "success": "Los grupos de investigación han sido agregados exitosamente." })
        return JSONResponse(content=content, status_code=200)
    except Exception as e:
        print(e)
        content = jsonable_encoder(content = { "error": "La información de los grupos de investigación no pudo ser cargada." })
        return JSONResponse(content=content, status_code=500)
    

@app.get('/upload/programas')
def cargar_programas(db: Session = Depends(get_db)):
    programas = obtener_programas_academicos()
    try:
        db.bulk_save_objects(programas, update_changed_only=False)
        db.commit()
        content = jsonable_encoder({ "success": "Los programas académicos han sido agregados exitosamente." })
        return JSONResponse(content=content, status_code=200)
    except Exception as e:
        print(e)
        content = jsonable_encoder(content = { "error": "La información de los programas académicos no pudo ser cargada." })
        return JSONResponse(content=content, status_code=500)


@app.post('/registro', response_model=UserSchema, response_model_exclude={'clave'}, status_code=201)
def register_user(user: BaseUser, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)


@app.post('/login', response_model=UserSchema, response_model_exclude={'clave'}, status_code=200)
def login(user: UserLoginSchema, db: Session = Depends(get_db)):
    # get password from db
    db_user = get_user_by_email(db, email=user.email)
    password = decode_password(db_user.clave)

    # user not exists
    if not db_user:
        raise HTTPException(status_code=404, detail="Este usuario no existe")
    
    # wrong password
    if user.clave != password:
        raise HTTPException(status_code=401, detail="Las credenciales no son válidas")
    return db_user


# @app.post("/users/", response_model=User)
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     db_user = get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return create_user(db=db, user=user)


# @app.get("/users/", response_model=list[User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = get_users(db, skip=skip, limit=limit)
#     return users

# TODO => obtener un único usuario => relación con url params => búsqueda por ID
# @app.get("/users/{user_id}", response_model=User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @app.post("/users/{user_id}/items/", response_model=Item)
# def create_item_for_user(
#     user_id: int, item: ItemCreate, db: Session = Depends(get_db)
# ):
#     return create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=list[Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = get_items(db, skip=skip, limit=limit)
#     return items
