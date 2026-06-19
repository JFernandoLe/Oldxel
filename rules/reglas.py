def fila_vacia(fila):

    for valor in fila:

        if str(valor).strip():
            return False

    return True


def procesar_fila(
    fila,
    config
):

    if (
        config["eliminar_filas_vacias"]
        and fila_vacia(fila)
    ):
        return None

    return fila