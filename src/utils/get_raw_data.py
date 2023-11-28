import sys
sys.path.append('.')

from models import Facultad, GrupoInv, Programa

def obtener_grupos_inv():
    route = r'D:\Freelance\grupos_investigacion.txt'
    data = get_raw_data(route)
    grupos_inv = [GrupoInv(nombre=item) for item in data]

    return grupos_inv


def obtener_programas_academicos():
    route = r'D:\Freelance\programas_academicos.txt'
    data = get_raw_data(route)
    programas_academicos = [Programa(nombre=item, facultad_id=None) for item in data]

    return programas_academicos


def obtener_facultades():
    route = r'D:\Freelance\facultades.txt'
    data = get_raw_data(route)
    facultades = [Facultad(nombre=item) for item in data]

    return facultades


def get_raw_data(route):
    data = []
    with open(route, encoding='utf8') as file:
        for line in file:
            data.append(line.strip()) 

    return data


programas = obtener_programas_academicos()
facultades = obtener_facultades()
grupos = obtener_grupos_inv()
#print(grupos)
#print([item.nombre for item in facultades])
#print([[item.nombre, item.facultad_id] for item in programas])