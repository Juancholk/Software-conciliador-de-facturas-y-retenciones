"""Reglas de negocio de la conciliación entre facturas y contabilidad.

Este módulo no depende de FastAPI: recibe listas de diccionarios y devuelve
un diccionario con el resumen, el detalle y las advertencias.
"""

from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation

from app.causas import ADVERTENCIAS, CAUSAS
from app.config import (
    COLUMNAS_FACTURAS, ESTADOS_VALIDOS, TARIFAS_IVA_VALIDAS, TOLERANCIA,
)

CORRECTA = "Correcta"
CON_INCONSISTENCIA = "Con inconsistencia"

# Utilidades de conversión

def a_decimal(valor: str) -> Decimal | None:
    """Convierte un texto a Decimal. Devuelve None si está vacío o no es numérico."""
    texto = (valor or "").strip().replace("%", "").replace(" ", "")
    if not texto:
        return None
    if "," in texto and "." in texto:      # formato 1.234.567,50
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:                      # formato 0,19
        texto = texto.replace(",", ".")
    try:
        return Decimal(texto)
    except InvalidOperation:
        return None


def normalizar_tarifa(tarifa: Decimal | None) -> Decimal | None:
    """Convierte 19 o 19% en 0.19. Los valores entre 0 y 1 se dejan igual."""
    if tarifa is None:
        return None
    return tarifa / 100 if tarifa > 1 else tarifa


def es_fecha_valida(valor: str) -> bool:
    try:
        date.fromisoformat(valor)
        return True
    except ValueError:
        return False


def a_numero(valor: Decimal | None):
    """Convierte Decimal a int o float para poder enviarlo como JSON."""
    if valor is None:
        return None
    return int(valor) if valor == valor.to_integral_value() else float(valor)


def causa(codigo: str, detalle: str = "") -> dict:
    return {"codigo": codigo, "descripcion": CAUSAS[codigo], "detalle": detalle}


def formato_pesos(valor: Decimal) -> str:
    return f"{a_numero(valor):,}".replace(",", ".")

# Reglas

def validar_campos(factura: dict) -> list[dict]:
    vacios = [c for c in COLUMNAS_FACTURAS if not factura.get(c, "")]
    if vacios:
        return [causa("CAMPO_VACIO", f"Campos vacíos: {', '.join(vacios)}")]
    return []


def validar_formatos(factura: dict) -> list[dict]:
    """Detecta valores no vacíos que no se pueden interpretar."""
    invalidos = []
    for campo in ["base_gravable", "tarifa_iva", "valor_iva",
                  "tarifa_retencion", "valor_retencion", "total_factura"]:
        if factura.get(campo) and a_decimal(factura[campo]) is None:
            invalidos.append(campo)
    if factura.get("fecha_factura") and not es_fecha_valida(factura["fecha_factura"]):
        invalidos.append("fecha_factura")
    if invalidos:
        return [causa("VALOR_INVALIDO", f"Campos con formato no válido: {', '.join(invalidos)}")]
    return []


def comparar(codigo: str, esperado: Decimal, reportado: Decimal,
             etiquetas: tuple[str, str] = ("Esperado", "reportado")) -> tuple[list[dict], Decimal]:
    """Compara un valor esperado contra el reportado aplicando la tolerancia."""
    diferencia = reportado - esperado
    if abs(diferencia) > TOLERANCIA:
        detalle = (f"{etiquetas[0]} {formato_pesos(esperado)}, {etiquetas[1]} {formato_pesos(reportado)}, "
                   f"diferencia {formato_pesos(diferencia)}")
        return [causa(codigo, detalle)], abs(diferencia)
    return [], Decimal("0")


def validar_calculos(factura: dict) -> tuple[list[dict], dict, dict]:
    """Aplica las reglas de IVA, retención y total.

    Devuelve las causas encontradas, los cálculos para trazabilidad y
    el monto de las diferencias por concepto.
    """
    base = a_decimal(factura.get("base_gravable"))
    tarifa_iva = normalizar_tarifa(a_decimal(factura.get("tarifa_iva")))
    tarifa_ret = normalizar_tarifa(a_decimal(factura.get("tarifa_retencion")))
    iva_rep = a_decimal(factura.get("valor_iva"))
    ret_rep = a_decimal(factura.get("valor_retencion"))
    total_rep = a_decimal(factura.get("total_factura"))

    causas, diferencias = [], {"iva": Decimal("0"), "retencion": Decimal("0"), "total": Decimal("0")}

    iva_esp = base * tarifa_iva if base is not None and tarifa_iva is not None else None
    ret_esp = base * tarifa_ret if base is not None and tarifa_ret is not None else None
    total_esp = (base + iva_esp - ret_esp
                 if base is not None and iva_esp is not None and ret_esp is not None else None)

    if tarifa_iva is not None and tarifa_iva not in TARIFAS_IVA_VALIDAS:
        causas.append(causa("TARIFA_IVA_INVALIDA", f"Tarifa reportada: {a_numero(tarifa_iva * 100)}%"))

    if iva_esp is not None and iva_rep is not None:
        c, d = comparar("DIF_IVA", iva_esp, iva_rep)
        causas += c
        diferencias["iva"] = d

    if ret_esp is not None and ret_rep is not None:
        c, d = comparar("DIF_RETENCION", ret_esp, ret_rep)
        causas += c
        diferencias["retencion"] = d

    # El total se compara contra valores recalculados para señalar la causa raíz
    if total_esp is not None and total_rep is not None:
        c, d = comparar("DIF_TOTAL", total_esp, total_rep)
        causas += c
        diferencias["total"] = d

    calculos = {
        "iva_esperado": a_numero(iva_esp), "iva_reportado": a_numero(iva_rep),
        "retencion_esperada": a_numero(ret_esp), "retencion_reportada": a_numero(ret_rep),
        "total_esperado": a_numero(total_esp), "total_reportado": a_numero(total_rep),
    }
    return causas, calculos, diferencias


def validar_contabilidad(factura: dict, registros: list[dict]) -> tuple[list[dict], dict, Decimal]:
    """Cruza la factura contra sus registros contables."""
    if not registros:
        return [causa("SIN_REGISTRO_CONTABLE")], {"registros": 0, "valor_contabilizado": None}, Decimal("0")

    causas = []

    estados_invalidos = sorted({r.get("estado", "") or "(vacío)" for r in registros
                                if r.get("estado", "").lower() not in ESTADOS_VALIDOS})
    if estados_invalidos:
        causas.append(causa("ESTADO_PENDIENTE", f"Estado: {', '.join(estados_invalidos)}"))

    total_debito = Decimal("0")
    en_cero = 0
    for r in registros:
        debito = a_decimal(r.get("valor_debito")) or Decimal("0")
        credito = a_decimal(r.get("valor_credito")) or Decimal("0")
        total_debito += debito
        if abs(debito - credito) > TOLERANCIA:
            causas.append(causa(
                "DEBITO_CREDITO_DIFERENTE",
                f"Cuenta {r.get('cuenta_contable')}: débito {formato_pesos(debito)}, "
                f"crédito {formato_pesos(credito)}",
            ))
        if debito == 0 and credito == 0:
            en_cero += 1

    if en_cero:
        causas.append(causa("REGISTRO_CONTABLE_EN_CERO",
                            f"{en_cero} de {len(registros)} registros con valor 0"))

    diferencia = Decimal("0")
    total_factura = a_decimal(factura.get("total_factura"))
    if total_factura is not None:
        c, diferencia = comparar("DIF_VALOR_CONTABLE", total_factura, total_debito,
                                 ("Total factura", "contabilizado"))
        causas += c

    info = {"registros": len(registros), "valor_contabilizado": a_numero(total_debito)}
    return causas, info, diferencia

# Proceso principal

def conciliar(facturas: list[dict], contabilidad: list[dict]) -> dict:
    conteo_ids = Counter(f.get("id_factura", "") for f in facturas)

    filas_por_id = defaultdict(list)
    for numero_fila, factura in enumerate(facturas, start=2):
        filas_por_id[factura.get("id_factura", "")].append(numero_fila)

    registros_por_factura = defaultdict(list)
    for registro in contabilidad:
        registros_por_factura[registro.get("id_factura", "")].append(registro)

    detalle = []
    por_causa = Counter()
    montos = {"iva": Decimal("0"), "retencion": Decimal("0"),
              "total": Decimal("0"), "valor_contable": Decimal("0")}

    for numero_fila, factura in enumerate(facturas, start=2):
        id_factura = factura.get("id_factura", "")
        causas = validar_campos(factura) + validar_formatos(factura)

        if id_factura and conteo_ids[id_factura] > 1:
            otras = [str(n) for n in filas_por_id[id_factura] if n != numero_fila]
            causas.append(causa(
                "ID_DUPLICADO",
                f"Aparece {conteo_ids[id_factura]} veces en el archivo. "
                f"Revisar también la fila {', '.join(otras)}",
            ))

        causas_calc, calculos, difs = validar_calculos(factura)
        causas_cont, contable, dif_cont = validar_contabilidad(
            factura, registros_por_factura.get(id_factura, []))
        causas += causas_calc + causas_cont

        for concepto, valor in difs.items():
            montos[concepto] += valor
        montos["valor_contable"] += dif_cont

        codigos = {c["codigo"] for c in causas}
        por_causa.update(codigos)

        detalle.append({
            "fila": numero_fila,
            "id_factura": id_factura,
            "nit_proveedor": factura.get("nit_proveedor", ""),
            "fecha_factura": factura.get("fecha_factura", ""),
            "concepto": factura.get("concepto", ""),
            "base_gravable": a_numero(a_decimal(factura.get("base_gravable"))),
            "estado": CON_INCONSISTENCIA if causas else CORRECTA,
            "causas": causas,
            "calculos": calculos,
            "contabilidad": contable,
        })

    # Cruce inverso: registros contables cuya factura no existe en el archivo de facturas
    ids_facturas = set(conteo_ids)
    registros_sin_factura = []
    for numero_fila, registro in enumerate(contabilidad, start=2):
        id_factura = registro.get("id_factura", "")
        if id_factura not in ids_facturas:
            registros_sin_factura.append({
                "fila": numero_fila,
                "id_factura": id_factura,
                "fecha_contabilizacion": registro.get("fecha_contabilizacion", ""),
                "cuenta_contable": registro.get("cuenta_contable", ""),
                "valor_debito": a_numero(a_decimal(registro.get("valor_debito"))),
                "causa": causa("REGISTRO_SIN_FACTURA",
                               "El registro no tiene una factura que lo soporte"),
            })

    # Advertencias (no cambian el estado de las facturas)
    advertencias = []
    periodos = sorted({r["fecha_contabilizacion"][:7] for r in contabilidad
                       if es_fecha_valida(r.get("fecha_contabilizacion", ""))})
    if len(periodos) > 1:
        advertencias.append({
            "codigo": "VARIOS_PERIODOS",
            "descripcion": ADVERTENCIAS["VARIOS_PERIODOS"],
            "detalle": f"Periodos encontrados: {', '.join(periodos)}",
        })

    con_inconsistencia = sum(1 for d in detalle if d["estado"] == CON_INCONSISTENCIA)
    resumen = {
        "registros_leidos": len(facturas),
        "facturas_unicas": len(ids_facturas - {""}),
        "correctas": len(detalle) - con_inconsistencia,
        "con_inconsistencia": con_inconsistencia,
        "por_causa": dict(por_causa.most_common()),
        "monto_diferencias": {k: a_numero(v) for k, v in montos.items()},
        "registros_contables_leidos": len(contabilidad),
        "registros_contables_sin_factura": len(registros_sin_factura),
    }

    return {
        "resumen": resumen,
        "detalle": detalle,
        "registros_sin_factura": registros_sin_factura,
        "advertencias": advertencias,
    }
