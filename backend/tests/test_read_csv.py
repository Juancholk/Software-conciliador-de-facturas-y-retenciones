import pytest

from app.config import COLUMNAS_CONTABILIDAD
from app.services.read_csv import ErrorArchivo, leer_csv

ENCABEZADO = ",".join(COLUMNAS_CONTABILIDAD)
FILA = "F-1,2026-03-12,511010,CC1001,100,100,Contabilizada"


def test_lee_archivo_con_bom():
    contenido = ("﻿" + ENCABEZADO + "\n" + FILA).encode("utf-8")
    filas = leer_csv(contenido, "contabilidad", COLUMNAS_CONTABILIDAD)
    assert filas[0]["id_factura"] == "F-1"


def test_detecta_separador_punto_y_coma():
    contenido = (ENCABEZADO.replace(",", ";") + "\n" + FILA.replace(",", ";")).encode()
    filas = leer_csv(contenido, "contabilidad", COLUMNAS_CONTABILIDAD)
    assert filas[0]["estado"] == "Contabilizada"


def test_archivo_vacio():
    with pytest.raises(ErrorArchivo, match="vacío"):
        leer_csv(b"   ", "contabilidad", COLUMNAS_CONTABILIDAD)


def test_columnas_faltantes_indica_cuales():
    contenido = b"id_factura,estado\nF-1,Contabilizada"
    with pytest.raises(ErrorArchivo, match="fecha_contabilizacion"):
        leer_csv(contenido, "contabilidad", COLUMNAS_CONTABILIDAD)


def test_archivo_solo_con_encabezado():
    with pytest.raises(ErrorArchivo, match="no tiene registros"):
        leer_csv(ENCABEZADO.encode(), "contabilidad", COLUMNAS_CONTABILIDAD)
