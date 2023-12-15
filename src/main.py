from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import ResponseValidationError
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Annotated
from datetime import datetime, date
import requests

from crud import get_user_by_email, create_user, create_propuesta, get_dashboard_totales, get_facultades, get_programas, get_grupos_inv, get_proyectos, get_convocatorias, get_usuarios, get_propuestas, get_informacion_propuesta # , get_users, get_user, create_user_item, get_items
from models import Base, Usuario, Facultad, Programa, GrupoInv, Convocatoria, Rol, Propuesta, Estado, Proyecto
from schemas import UserLoginSchema, UserSchema, CreateUserSchema, UserResponseSchema, BasePropuestaSchema, BaseUser, BaseConvocatoria, FacultadSchema, ProgramaSchema, GrupoInvSchema, ConvocatoriaSchema # , ItemCreate, Item, User, UserCreate
from database import SessionLocal, engine

# utils >>>
from src.utils.password_generator import decode_password
from src.utils.bunny_cdn import secure_filename

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

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


@app.get('/dashboard/proyectos-ejecutados', status_code=200)
def _proyectos_ejecutados(programa_id: int = None, db: Session = Depends(get_db)):
    print(f'Valor del programa_id: {programa_id}')
    current_year = date.today().year
    years = [current_year - 6, current_year - 5, current_year - 4, current_year - 3, current_year - 2, current_year - 1, current_year]
    current_year = str(current_year)
    
    # grupos_inv = db.query(GrupoInv).all()

    # for year in years:
    #     query = (
    #         db.query(
    #             GrupoInv.id,
    #             GrupoInv.nombre,
    #             func.count(Proyecto.id)
    #         )
    #         .outerjoin(Proyecto, GrupoInv.nombre == Proyecto.grupo_investigacion)
    #         .filter(Proyecto.anio == str(year))
    #         .group_by(GrupoInv.id, Proyecto.anio)
    #         .order_by(GrupoInv.id.asc())
    #     )
    #     print(query.all())
    
    # Query
    query = (
        db.query(
            GrupoInv.id,
            GrupoInv.nombre,
            func.count(Proyecto.id)
        )
        .outerjoin(Proyecto, GrupoInv.nombre == Proyecto.grupo_investigacion)
        .filter(Proyecto.anio == '2022')
        .group_by(GrupoInv.id, Proyecto.anio)
        .order_by(GrupoInv.id.asc())
    )

    # Execute the query
    result = query.all()
    print(result)
    # results = db.query(Proyecto.grupo_investigacion, func.count(Proyecto.grupo_investigacion)).filter(and_(Proyecto.anio == '2022')).group_by(Proyecto.grupo_investigacion).all()

    # for grupo_inv, count in results:
    #     print(f"Grupo Inv: {grupo_inv}, Count: {count}")

    return JSONResponse(content='buena mostro')


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
            'url_archivo_propuesta': url,
        }

        return create_propuesta(db=db, data=data)


@app.post('/login', response_model=UserResponseSchema, response_model_exclude={'clave'}, status_code=200)
def _login(user: UserLoginSchema, db: Session = Depends(get_db)):
    # get password from db
    db_user = get_user_by_email(db, email=user.email)
    # user not exists
    if not db_user:
        return JSONResponse(content='El usuario no existe', status_code=404)
        # raise HTTPException(status_code=404, detail="El usuario no existe")

    password = decode_password(db_user.clave)
    # wrong password
    if user.clave != password:
        return JSONResponse(content='Las credenciales no son válidas', status_code=401)
    return db_user


@app.get('/estados', status_code=200)
def _estados(db: Session = Depends(get_db)):
    # obtener los estados
    return db.query(Estado).all()


@app.get('/dashboard/totales', status_code=200)
def _dashboard_totales(db: Session = Depends(get_db)):
    data = get_dashboard_totales(db)
    return data


@app.get('/info-propuesta', status_code=200)
def _get_informacion_propuesta(db: Session = Depends(get_db)):
    '''
    este endpoint tiene como finalidad obtener grupos, facultades y programas registradas en la bd
    '''
    data = get_informacion_propuesta(db)
    return data


@app.get("/convocatorias", response_model=list[ConvocatoriaSchema])
def _obtener_convocatorias(skip: int = 0, limit: int = 0, db: Session = Depends(get_db)):
    items = get_convocatorias(db, skip=skip, limit=limit)
    return items


@app.get("/proyectos")
def _obtener_proyectos(skip: int = 0, limit: int = 0, db: Session = Depends(get_db)):
    total_proyectos = db.query(Proyecto).count()
    if limit != 0:
        proyectos = db.query(Proyecto).offset(skip).limit(limit).all()
    else:
        proyectos = db.query(Proyecto).offset(skip).all()
    return { 'proyectos': proyectos, 'total_proyectos': total_proyectos }


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


@app.get("/propuestas", response_model_exclude={'usuario.clave'}, response_model=list[BasePropuestaSchema])
def _obtener_propuestas(usuario_id: int = 0, convocatoria_id: int = 0, db: Session = Depends(get_db)):
    return get_propuestas(db=db, usuario_id=usuario_id, convocatoria_id=convocatoria_id)


@app.post("/update/estado-propuesta", status_code=200)
def _actualizar_estado_propuesta(propuesta_id: Annotated[str, Form()], estado_id: Annotated[str, Form()], observaciones: str = Form(None), db: Session = Depends(get_db)):
    db.query(Propuesta).filter(Propuesta.id == propuesta_id).update({Propuesta.estado_id: estado_id, Propuesta.observaciones: observaciones})
    db.commit()
    return JSONResponse(content='La propuesta ha sido actualizada')


@app.post("/update/calificacion-propuesta", status_code=200)
async def _actualizar_calificacion_propuesta(puntaje: Annotated[str, Form()], estado_id: Annotated[int, Form()], propuesta_id: Annotated[int, Form()], file: UploadFile = File(...), db: Session = Depends(get_db)):
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

        db.query(Propuesta).filter(Propuesta.id == propuesta_id).update({Propuesta.estado_id: estado_id, Propuesta.calificacion: puntaje, Propuesta.url_archivo_calificacion: url})
        db.commit()
        return JSONResponse(content='La propuesta ha sido actualizada exitosamente')
    # db.query(Propuesta).filter(Propuesta.id == propuesta_id).update({Propuesta.estado_id: estado_id, Propuesta.observaciones: observaciones})
    # db.commit()


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
    import re
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
        idx = url.rfind('/') + 1
        filename = url[idx::]

        def fetch_data(r):
            for chunk in r.iter_content(chunk_size=8192):
                yield chunk

        return StreamingResponse(fetch_data(response), media_type=response.headers.get('content-type'), headers={'Content-Disposition': f'attachment; filename={filename}'})
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
