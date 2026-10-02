"""Tests de las reglas de negocio. Cada test construye un caso pequeño a mano."""

from app.services.conciliator import CON_INCONSISTENCIA, CORRECTA, conciliar


def factura(**cambios) -> dict:
    """Factura correcta: 1.000.000 + IVA 19% (190.000) − retención 4% (40.000) = 1.150.000."""
    base = {
        "id_factura": "F-1", "nit_proveedor": "900111222", "fecha_factura": "2026-03-10",
        "concepto": "Servicio", "base_gravable": "1000000", "tarifa_iva": "0.19",
        "valor_iva": "190000", "tarifa_retencion": "0.04", "valor_retencion": "40000",
        "total_factura": "1150000",
    }
    base.update(cambios)
    return base


def registro(**cambios) -> dict:
    base = {
        "id_factura": "F-1", "fecha_contabilizacion": "2026-03-12", "cuenta_contable": "511010",
        "centro_costo": "CC1001", "valor_debito": "1150000", "valor_credito": "1150000",
        "estado": "Contabilizada",
    }
    base.update(cambios)
    return base


def codigos(resultado: dict, indice: int = 0) -> set[str]:
    return {c["codigo"] for c in resultado["detalle"][indice]["causas"]}


# --- Caso base -------------------------------------------------------------

def test_factura_correcta():
    r = conciliar([factura()], [registro()])
    assert r["detalle"][0]["estado"] == CORRECTA
    assert r["detalle"][0]["causas"] == []
    assert r["resumen"]["correctas"] == 1


# --- Regla 1 y 2: cálculos ---------------------------------------------------

def test_iva_mal_calculado_solo_marca_iva():
    # El IVA reportado está mal, pero el total se calculó con el IVA correcto
    r = conciliar([factura(valor_iva="180000")], [registro()])
    assert codigos(r) == {"DIF_IVA"}
    assert r["detalle"][0]["calculos"]["iva_esperado"] == 190000


def test_total_mal_calculado():
    r = conciliar([factura(total_factura="1200000")], [registro(valor_debito="1200000", valor_credito="1200000")])
    assert codigos(r) == {"DIF_TOTAL"}
    assert r["resumen"]["monto_diferencias"]["total"] == 50000


def test_retencion_mal_calculada():
    r = conciliar([factura(valor_retencion="30000", total_factura="1160000")],
                  [registro(valor_debito="1160000", valor_credito="1160000")])
    assert "DIF_RETENCION" in codigos(r)


def test_tarifa_iva_invalida():
    r = conciliar([factura(tarifa_iva="0.16", valor_iva="160000", total_factura="1120000")],
                  [registro(valor_debito="1120000", valor_credito="1120000")])
    assert codigos(r) == {"TARIFA_IVA_INVALIDA"}


def test_tarifa_en_porcentaje_se_normaliza():
    r = conciliar([factura(tarifa_iva="19", tarifa_retencion="4%")], [registro()])
    assert r["detalle"][0]["estado"] == CORRECTA


def test_tolerancia_de_un_peso():
    dentro = conciliar([factura(valor_iva="190001", total_factura="1150001")],
                       [registro(valor_debito="1150001", valor_credito="1150001")])
    fuera = conciliar([factura(valor_iva="190002")], [registro()])
    assert dentro["detalle"][0]["estado"] == CORRECTA
    assert "DIF_IVA" in codigos(fuera)


# --- Datos de la factura -----------------------------------------------------

def test_campo_vacio():
    r = conciliar([factura(nit_proveedor="")], [registro()])
    assert codigos(r) == {"CAMPO_VACIO"}
    assert "nit_proveedor" in r["detalle"][0]["causas"][0]["detalle"]


def test_valor_no_numerico():
    r = conciliar([factura(base_gravable="abc")], [registro()])
    assert "VALOR_INVALIDO" in codigos(r)


def test_id_duplicado_marca_todas_las_ocurrencias():
    r = conciliar([factura(), factura(nit_proveedor="900333444")], [registro()])
    assert "ID_DUPLICADO" in codigos(r, 0)
    assert "ID_DUPLICADO" in codigos(r, 1)
    assert r["resumen"]["registros_leidos"] == 2
    assert r["resumen"]["facturas_unicas"] == 1


# --- Regla 3: contabilidad ---------------------------------------------------

def test_factura_sin_registro_contable():
    r = conciliar([factura()], [registro(id_factura="OTRA")])
    assert codigos(r) == {"SIN_REGISTRO_CONTABLE"}


def test_estado_pendiente():
    r = conciliar([factura()], [registro(estado="Pendiente")])
    assert codigos(r) == {"ESTADO_PENDIENTE"}


def test_debito_y_credito_diferentes():
    r = conciliar([factura()], [registro(valor_credito="1000000")])
    assert codigos(r) == {"DEBITO_CREDITO_DIFERENTE"}


def test_valor_contable_diferente_al_total():
    r = conciliar([factura()], [registro(valor_debito="1100000", valor_credito="1100000")])
    assert codigos(r) == {"DIF_VALOR_CONTABLE"}


def test_registro_contable_en_cero():
    r = conciliar([factura()], [registro(), registro(valor_debito="0", valor_credito="0")])
    assert codigos(r) == {"REGISTRO_CONTABLE_EN_CERO"}


# --- Regla 4 y 5: clasificación y resumen -------------------------------------

def test_una_factura_puede_tener_varias_causas():
    r = conciliar([factura(valor_iva="100000")], [registro(estado="Pendiente")])
    assert codigos(r) == {"DIF_IVA", "ESTADO_PENDIENTE"}
    assert r["detalle"][0]["estado"] == CON_INCONSISTENCIA


def test_resumen_cuenta_por_causa():
    r = conciliar([factura(), factura(id_factura="F-2", valor_iva="1")], [registro()])
    assert r["resumen"]["con_inconsistencia"] == 1
    assert r["resumen"]["por_causa"]["SIN_REGISTRO_CONTABLE"] == 1
    assert r["resumen"]["por_causa"]["DIF_IVA"] == 1


# --- Advertencias --------------------------------------------------------------

def test_registro_contable_sin_factura():
    r = conciliar([factura()], [registro(), registro(id_factura="F-99")])
    assert r["resumen"]["registros_contables_sin_factura"] == 1
    sin_factura = r["registros_sin_factura"][0]
    assert sin_factura["id_factura"] == "F-99"
    assert sin_factura["fila"] == 3
    assert sin_factura["causa"]["codigo"] == "REGISTRO_SIN_FACTURA"


def test_varios_periodos_es_advertencia():
    r = conciliar([factura(), factura(id_factura="F-2")],
                  [registro(), registro(id_factura="F-2", fecha_contabilizacion="2026-04-02")])
    assert r["resumen"]["correctas"] == 2
    assert any(a["codigo"] == "VARIOS_PERIODOS" for a in r["advertencias"])
