import json

def cargar_configuracion():

    with open(
        "config/configuracion.json",
        "r",
        encoding="utf-8"
    ) as archivo:

        return json.load(archivo)