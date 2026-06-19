import os
import csv
from pathlib import Path

from python_calamine import CalamineWorkbook
from openpyxl import Workbook
from tqdm import tqdm

# ==================================================
# CONFIGURACION
# ==================================================

CARPETA_ENTRADA = r"./ExcelViejos"
CARPETA_SALIDA = r"./Convertidos"

FORMATO_SALIDA = "xlsx"  # "xlsx" o "csv"

LIMITE_XLSX = 1_048_576
MAX_DATOS_XLSX = 1000  # encabezado ocupa una fila

# ==================================================
# UTILIDADES
# ==================================================

def encontrar_encabezado(rows):
    """
    Busca la fila que contiene Fecha y Agente.
    """
    for idx, row in enumerate(rows):
        row_str = [str(x).strip() for x in row]

        if "Fecha" in row_str and "Agente" in row_str:
            return idx

    raise Exception("No se encontró la fila de encabezado")


def crear_xlsx(nombre_base, parte, encabezado):

    ruta = Path(CARPETA_SALIDA) / f"{nombre_base}_Parte{parte}.xlsx"

    wb = Workbook(write_only=True)
    ws = wb.create_sheet("Datos")

    ws.append(encabezado)

    return wb, ws, ruta


# ==================================================
# XLSX
# ==================================================

def convertir_a_xlsx(archivo):

    wb_calamine = CalamineWorkbook.from_path(str(archivo))

    hojas = wb_calamine.sheet_names

    # -------------------------------
    # Primera hoja
    # -------------------------------

    sheet = wb_calamine.get_sheet_by_name(hojas[0])
    rows = sheet.to_python()

    fila_encabezado = encontrar_encabezado(rows)

    encabezado = rows[fila_encabezado]

    parte = 1
    filas_actuales = 0

    wb_out, ws_out, ruta_salida = crear_xlsx(
        archivo.stem,
        parte,
        encabezado
    )

    # -------------------------------
    # Recorrer hojas
    # -------------------------------

    for indice_hoja, nombre_hoja in enumerate(hojas):

        sheet = wb_calamine.get_sheet_by_name(nombre_hoja)
        rows = sheet.to_python()

        if indice_hoja == 0:
            inicio = fila_encabezado + 2
        else:
            inicio = 0

        for fila in rows[inicio:]:

            if filas_actuales >= MAX_DATOS_XLSX:

                wb_out.save(ruta_salida)

                parte += 1
                filas_actuales = 0

                wb_out, ws_out, ruta_salida = crear_xlsx(
                    archivo.stem,
                    parte,
                    encabezado
                )

            ws_out.append(fila)
            filas_actuales += 1

    wb_out.save(ruta_salida)


# ==================================================
# CSV
# ==================================================

def convertir_a_csv(archivo):

    wb_calamine = CalamineWorkbook.from_path(str(archivo))

    hojas = wb_calamine.sheet_names

    ruta_csv = Path(CARPETA_SALIDA) / f"{archivo.stem}.csv"

    with open(
        ruta_csv,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

        # ---------------------------
        # Encabezado
        # ---------------------------

        sheet = wb_calamine.get_sheet_by_name(hojas[0])
        rows = sheet.to_python()

        fila_encabezado = encontrar_encabezado(rows)

        encabezado = rows[fila_encabezado]

        writer.writerow(encabezado)

        # ---------------------------
        # Datos
        # ---------------------------

        for indice_hoja, nombre_hoja in enumerate(hojas):

            sheet = wb_calamine.get_sheet_by_name(nombre_hoja)
            rows = sheet.to_python()

            if indice_hoja == 0:
                inicio = fila_encabezado + 2
            else:
                inicio = 0

            for fila in rows[inicio:]:
                writer.writerow(fila)


# ==================================================
# PROCESAMIENTO
# ==================================================

def procesar_archivo(archivo):

    print(f"\nProcesando: {archivo.name}")

    if FORMATO_SALIDA.lower() == "xlsx":
        convertir_a_xlsx(archivo)

    elif FORMATO_SALIDA.lower() == "csv":
        convertir_a_csv(archivo)

    else:
        raise ValueError(
            "FORMATO_SALIDA debe ser 'xlsx' o 'csv'"
        )


def main():

    Path(CARPETA_SALIDA).mkdir(
        parents=True,
        exist_ok=True
    )

    archivos = list(
        Path(CARPETA_ENTRADA).glob("*.xls")
    )

    print(f"\nArchivos encontrados: {len(archivos)}")

    for archivo in tqdm(archivos):

        try:
            procesar_archivo(archivo)

        except Exception as e:

            print(
                f"\nERROR en {archivo.name}"
            )
            print(e)

    print("\nProceso terminado.")


if __name__ == "__main__":
    main()