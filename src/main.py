from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
import requests
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from datetime import datetime, date

from crud import get_user_by_email, create_user, create_convocatoria, create_propuesta, get_dashboard_totales, get_facultades, get_programas, get_grupos_inv, get_proyectos, get_convocatorias, get_usuarios, get_propuestas # , get_users, get_user, create_user_item, get_items
from models import Base, Usuario, Facultad, Programa, GrupoInv, Convocatoria, Rol, Propuesta
from schemas import UserLoginSchema, UserSchema, CreateUserSchema, UserResponseSchema, PropuestaSchema, BaseUser, BaseConvocatoria, FacultadSchema, ProgramaSchema, GrupoInvSchema, ConvocatoriaSchema # , ItemCreate, Item, User, UserCreate
from database import SessionLocal, engine
from sqlalchemy.exc import IntegrityError

# utils >>>
from src.utils.password_generator import get_encrypted_pass, decode_password
from src.utils.excel_to_database import get_projects_from_excel
from src.utils.get_raw_data import obtener_facultades, obtener_grupos_inv, obtener_programas_academicos
from src.utils.bunny_cdn import secure_filename

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def _home(db: Session = Depends(get_db)):
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
def _cargar_facultades(db: Session = Depends(get_db)):
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
def _cargar_grupos_inv(db: Session = Depends(get_db)):
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
def _cargar_programas(db: Session = Depends(get_db)):
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


@app.post('/registro/usuario', response_model=UserResponseSchema, response_model_exclude={'clave'}, status_code=201)
def _register_user(user: CreateUserSchema, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)


@app.post('/registro/convocatoria', response_model=ConvocatoriaSchema, status_code=201)
async def _register_convocatoria(titulo: Annotated[str, Form()], descripcion: Annotated[str, Form()], fecha_inicio: Annotated[date, Form()], fecha_limite: Annotated[date, Form()], fecha_inicio_evaluacion: Annotated[date, Form()], fecha_fin_evaluacion: Annotated[date, Form()], fecha_publicacion_resultados: Annotated[date, Form()], tipo_convocatoria: Annotated[str, Form()], file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        STORAGE_ZONE_NAME = 'finu-storage'
        ACCESS_KEY = '64e5ab92-d290-4a0b-96cd1770b46c-2bb2-4201'
        BASE_URL = "storage.bunnycdn.com"
        NAME = secure_filename(file.filename)

        headers = {
        "AccessKey": ACCESS_KEY,
        "Content-Type": "application/octet-stream",
        "accept": "application/json"
        }

        with open(file.filename, 'wb'):
            content = await file.read()
            url = f"https://{BASE_URL}/{STORAGE_ZONE_NAME}/{NAME}"
            response = requests.put(url, headers=headers, data=content)

            db_convocatoria = Convocatoria(
                titulo=titulo,
                descripcion=descripcion,
                fecha_inicio=fecha_inicio,
                fecha_limite=fecha_limite,
                fecha_inicio_evaluacion=fecha_inicio_evaluacion,
                fecha_fin_evaluacion=fecha_fin_evaluacion,
                fecha_publicacion_resultados=fecha_publicacion_resultados,
                url_archivo=url,
                anio_convocatoria=str(datetime.now().year),
                tipo_convocatoria=tipo_convocatoria
            )

            db.add(db_convocatoria)
            db.commit()
            db.refresh(db_convocatoria)

            return db_convocatoria
    except Exception as e:
        return JSONResponse(content='Ha ocurrido un error al momento de cargar el archivo, por favor intente nuevamente', status_code=500)


@app.post('/registro/propuesta', status_code=201)
async def _register_propuesta(titulo: Annotated[str, Form()], descripcion: Annotated[str, Form()], usuario_id: Annotated[int, Form()], grupo_inv: Annotated[int, Form()], facultad: Annotated[int, Form()], programa: Annotated[int, Form()], convocatoria_id: Annotated[int, Form()], file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        STORAGE_ZONE_NAME = 'finu-storage'
        ACCESS_KEY = '64e5ab92-d290-4a0b-96cd1770b46c-2bb2-4201'
        BASE_URL = "storage.bunnycdn.com"
        NAME = secure_filename(file.filename)

        headers = {
        "AccessKey": ACCESS_KEY,
        "Content-Type": "application/octet-stream",
        "accept": "application/json"
        }

        with open(file.filename, 'wb'):
            content = await file.read()
            url = f"https://{BASE_URL}/{STORAGE_ZONE_NAME}/{NAME}"
            response = requests.put(url, headers=headers, data=content)

            data = {
                'titulo': titulo,
                'descripcion': descripcion,
                'usuario_id': usuario_id,
                'grupo_inv': grupo_inv,
                'facultad': facultad,
                'programa': programa,
                'convocatoria_id': convocatoria_id,
                'url_archivo': url,
            }

            return create_propuesta(db=db, data=data)
    except Exception as e:
        return JSONResponse(content='Ha ocurrido un error al momento de cargar el archivo, por favor intente nuevamente', status_code=500)


@app.post('/login', response_model=UserResponseSchema, response_model_exclude={'clave'}, status_code=200)
def _login(user: UserLoginSchema, db: Session = Depends(get_db)):
    # get password from db
    db_user = get_user_by_email(db, email=user.email)
    password = decode_password(db_user.clave)

    # user not exists
    if not db_user:
        raise HTTPException(status_code=404, detail="El usuario no existe")
    
    # wrong password
    if user.clave != password:
        raise HTTPException(status_code=401, detail="Las credenciales no son válidas")
    return db_user


@app.get('/dashboard/totales', status_code=200)
def _dashboard_totales(db: Session = Depends(get_db)):
    data = get_dashboard_totales(db)
    return data


@app.get("/convocatorias", response_model=list[ConvocatoriaSchema])
def _obtener_convocatorias(skip: int = 0, limit: int = 0, db: Session = Depends(get_db)):
    items = get_convocatorias(db, skip=skip, limit=limit)
    return items


@app.get("/facultades", response_model=list[FacultadSchema])
def _obtener_facultades(skip: int = 0, limit: int = 0, db: Session = Depends(get_db)):
    items = get_facultades(db, skip=skip, limit=limit)
    return items


@app.get("/programas", response_model=list[ProgramaSchema])
def _obtener_programas(skip: int = 0, limit: int = 0, db: Session = Depends(get_db)):
    items = get_programas(db, skip=skip, limit=limit)
    return items


@app.get("/grupos-inv", response_model=list[GrupoInvSchema])
def _obtener_grupos_inv(skip: int = 0, limit: int = 0, db: Session = Depends(get_db)):
    items = get_grupos_inv(db, skip=skip, limit=limit)
    return items


@app.get("/usuarios", response_model_exclude={'clave'}, response_model=list[UserResponseSchema])
def _obtener_usuarios(skip: int = 0, limit: int = 0, db: Session = Depends(get_db)):
    items = get_usuarios(db, skip=skip, limit=limit)
    return items


@app.get("/propuestas", response_model_exclude={'usuario.clave'}, response_model=list[PropuestaSchema])
def _obtener_propuestas(usuario_id: int = 0, convocatoria_id: int = 0, db: Session = Depends(get_db)):
    return get_propuestas(db=db, usuario_id=usuario_id, convocatoria_id=convocatoria_id)
    # return JSONResponse(content='buena mostro', status_code=200)


@app.post('/upload/files', status_code=201)
async def _upload(file: UploadFile = File(...)):
    try:
        STORAGE_ZONE_NAME = 'finu-storage'
        ACCESS_KEY = '64e5ab92-d290-4a0b-96cd1770b46c-2bb2-4201'
        BASE_URL = "storage.bunnycdn.com"
        NAME = secure_filename(file.filename)

        headers = {
        "AccessKey": ACCESS_KEY,
        "Content-Type": "application/octet-stream",
        "accept": "application/json"
        }

        with open(file.filename, 'wb'):
            content = await file.read()
            url = f"https://{BASE_URL}/{STORAGE_ZONE_NAME}/{NAME}"
            response = requests.put(url, headers=headers, data=content)
        return JSONResponse(content=f'El archivo {NAME} ha sido cargado exitosamente', status_code=response.status_code)
    except Exception as e:
        return JSONResponse(content='Ha ocurrido un error al momento de cargar el archivo, por favor intente nuevamente', status_code=500)


@app.get("/download")
def _download(url: str):
    from fastapi.responses import StreamingResponse
    import requests

    STORAGE_ZONE_NAME = 'finu-storage'
    ACCESS_KEY = '64e5ab92-d290-4a0b-96cd1770b46c-2bb2-4201'
    BASE_URL = "storage.bunnycdn.com"

    headers = {
        "AccessKey": ACCESS_KEY,
        "accept": "*/*",
    }

    try:
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()

        def fetch_data(r):
            for chunk in r.iter_content(chunk_size=8192):
                yield chunk

        return StreamingResponse(fetch_data(response), media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', headers={'Content-Disposition': f'attachment; filename={"archivo_de_prueba.docx"}'})
    except requests.exceptions.HTTPError:
        if response.status_code == 401:
            return JSONResponse(content='No tiene permisos para descargar este archivo', status_code=401)
        elif response.status_code == 404:
            return JSONResponse(content='El archivo no se encuentra en nuestra base de datos', status_code=404)
    
    # def fetch_data():
    #     with requests.get(url, stream=True, headers=headers) as r:
    #         r.raise_for_status()
    #         for chunk in r.iter_content(chunk_size=8192):
    #             yield chunk
    # return StreamingResponse(fetch_data(), media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', headers={'Content-Disposition': f'attachment; filename={"archivo_de_prueba.docx"}'})


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
