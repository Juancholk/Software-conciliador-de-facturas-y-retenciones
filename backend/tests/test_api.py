"""Tests de la API completa usando los archivos de prueba de la carpeta data/."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)
DATOS = Path(__file__).resolve().parents[2] / "data"


def enviar(facturas: Path, contabilidad: Path):
    with open(facturas, "rb") as f, open(contabilidad, "rb") as c:
        return cliente.post("/api/conciliar", files={
            "facturas": (facturas.name, f, "text/csv"),
            "contabilidad": (contabilidad.name, c, "text/csv"),
        })


def test_health():
    assert cliente.get("/api/health").json() == {"estado": "ok"}


def test_resultado_con_archivos_de_prueba():
    r = enviar(DATOS / "facturas.csv", DATOS / "contabilidad.csv")
    assert r.status_code == 200
    resumen = r.json()["resumen"]
    assert resumen["registros_leidos"] == 50
    assert resumen["facturas_unicas"] == 48
    assert resumen["correctas"] == 28
    assert resumen["con_inconsistencia"] == 22
    assert resumen["por_causa"] == {
        "REGISTRO_CONTABLE_EN_CERO": 7, "ID_DUPLICADO": 4, "SIN_REGISTRO_CONTABLE": 4,
        "DIF_TOTAL": 3, "ESTADO_PENDIENTE": 3, "CAMPO_VACIO": 3, "DIF_IVA": 2,
        "DIF_VALOR_CONTABLE": 2,
    }


def test_consulta_filtrada_por_estado():
    enviar(DATOS / "facturas.csv", DATOS / "contabilidad.csv")
    r = cliente.get("/api/resultados", params={"estado": "Correcta"})
    assert r.status_code == 200
    assert len(r.json()["detalle"]) == 28


def test_estado_de_filtro_invalido():
    enviar(DATOS / "facturas.csv", DATOS / "contabilidad.csv")
    assert cliente.get("/api/resultados", params={"estado": "Otro"}).status_code == 400


def test_archivo_que_no_es_csv():
    r = cliente.post("/api/conciliar", files={
        "facturas": ("facturas.txt", b"hola", "text/plain"),
        "contabilidad": ("contabilidad.csv", b"x", "text/csv"),
    })
    assert r.status_code == 400
    assert ".csv" in r.json()["detail"]


def test_columnas_faltantes_responde_400():
    r = cliente.post("/api/conciliar", files={
        "facturas": ("facturas.csv", b"id_factura,total_factura\nF-1,100", "text/csv"),
        "contabilidad": ("contabilidad.csv", (DATOS / "contabilidad.csv").read_bytes(), "text/csv"),
    })
    assert r.status_code == 400
    assert "nit_proveedor" in r.json()["detail"]
