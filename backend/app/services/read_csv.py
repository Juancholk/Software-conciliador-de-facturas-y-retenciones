"""Lectura y validación estructural de los archivos CSV."""

import csv
import io


class ErrorArchivo(Exception):
    """Error en la estructura de un archivo de entrada."""


def leer_csv(contenido: bytes, nombre: str, columnas_requeridas: list[str]) -> list[dict]:
    """Convierte el contenido de un CSV en una lista de diccionarios.

    - Acepta UTF-8 (con o sin BOM) y Latin-1.
    - Detecta si el separador es coma o punto y coma.
    - Normaliza los encabezados (sin espacios, en minúscula).
    - Verifica que estén todas las columnas requeridas.
    """
    if not contenido.strip():
        raise ErrorArchivo(f"El archivo de {nombre} está vacío.")

    try:
        texto = contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = contenido.decode("latin-1")

    primera_linea = texto.splitlines()[0]
    separador = ";" if primera_linea.count(";") > primera_linea.count(",") else ","

    lector = csv.DictReader(io.StringIO(texto), delimiter=separador)
    lector.fieldnames = [c.strip().lower() for c in (lector.fieldnames or [])]

    faltantes = [c for c in columnas_requeridas if c not in lector.fieldnames]
    if faltantes:
        raise ErrorArchivo(
            f"Al archivo de {nombre} le faltan las columnas: {', '.join(faltantes)}."
        )

    filas = []
    for fila in lector:
        # Se ignoran líneas completamente vacías
        if not any((v or "").strip() for v in fila.values()):
            continue
        filas.append({k: (v or "").strip() for k, v in fila.items() if k})

    if not filas:
        raise ErrorArchivo(f"El archivo de {nombre} no tiene registros.")

    return filas
