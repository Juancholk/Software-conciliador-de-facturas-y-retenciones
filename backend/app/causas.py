# Causas que marcan la factura como "Con inconsistencia"
CAUSAS = {
    # Datos de la factura
    "CAMPO_VACIO": "Campo obligatorio vacío",
    "VALOR_INVALIDO": "Valor numérico o fecha con formato no válido",
    "ID_DUPLICADO": "Id_Factura duplicado en el archivo de facturas",

    # Cálculos
    "TARIFA_IVA_INVALIDA": "Tarifa de IVA no válida (permitidas: 0%, 5%, 19%)",
    "DIF_IVA": "El valor del IVA no coincide con base × tarifa",
    "DIF_RETENCION": "El valor de la retención no coincide con base × tarifa",
    "DIF_TOTAL": "El total no coincide con base + IVA − retención",

    # Contabilidad
    "SIN_REGISTRO_CONTABLE": "La factura no tiene registro contable",
    "ESTADO_PENDIENTE": "El registro contable no está en estado Contabilizada",
    "DEBITO_CREDITO_DIFERENTE": "El débito y el crédito del registro no son iguales",
    "DIF_VALOR_CONTABLE": "El valor contabilizado no coincide con el total de la factura",
    "REGISTRO_CONTABLE_EN_CERO": "Existe un registro contable con valor en 0",
    "REGISTRO_SIN_FACTURA": "Registro contable sin factura que lo soporte",
}

# Advertencias: se informan, pero no cambian el estado de la factura
ADVERTENCIAS = {
    "VARIOS_PERIODOS": "Los registros pertenecen a más de un periodo contable",
}