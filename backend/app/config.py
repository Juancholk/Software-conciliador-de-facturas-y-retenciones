"""Parámetros de negocio del conciliador. Se cambian aquí sin tocar las reglas."""

from decimal import Decimal

# Diferencia máxima aceptada por redondeo (en pesos)
TOLERANCIA = Decimal("1")

# Tarifas de IVA vigentes en Colombia
TARIFAS_IVA_VALIDAS = {Decimal("0"), Decimal("0.05"), Decimal("0.19")}

# Estados contables que se consideran en firme (se comparan en minúscula)
ESTADOS_VALIDOS = {"contabilizada", "contabilizado"}

COLUMNAS_FACTURAS = [
    "id_factura", "nit_proveedor", "fecha_factura", "concepto", "base_gravable",
    "tarifa_iva", "valor_iva", "tarifa_retencion", "valor_retencion", "total_factura",
]

COLUMNAS_CONTABILIDAD = [
    "id_factura", "fecha_contabilizacion", "cuenta_contable", "centro_costo",
    "valor_debito", "valor_credito", "estado",
]
