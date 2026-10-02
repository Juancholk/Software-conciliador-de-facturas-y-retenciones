# Software-conciliador-de-facturas-y-retenciones
Software contable conciliador de facturas y retenciones.
## Supuestos

**Datos de entrada**
1. Las tarifas vienen en formato decimal (`0.19` = 19%). Si llega un valor mayor que 1 (`19`) se interpreta como porcentaje y se divide entre 100.
2. Todos los campos mínimos definidos en el enunciado son obligatorios. Un campo vacío marca la factura como *Con inconsistencia* sin detener el procesamiento del archivo.
3. Si los registros pertenecen a varios periodos contables, se muestra una advertencia indicando que se está trabajando con más de un periodo. Esto no cambia el estado de las facturas.

**Cálculos**
4. IVA esperado = `base_gravable × tarifa_iva`.
5. Retención esperada = `base_gravable × tarifa_retencion`.
6. Total esperado = `base_gravable + IVA esperado − retención esperada`, comparado contra `total_factura`. Se usan los valores recalculados y no los reportados, para que cada inconsistencia apunte a su causa: si solo el IVA reportado está mal, la factura se marca por IVA y no también por total.
7. Tarifas de IVA válidas: 0%, 5% y 19%.
8. Se acepta una tolerancia de ±1 peso por redondeo.

**Facturas**
9. Si un `id_factura` aparece más de una vez en el archivo de facturas, todas sus ocurrencias se marcan como "Id_Factura duplicado".

**Contabilidad**
10. Solo el estado `Contabilizada` es válido. El estado `Pendiente` se marca como inconsistencia.
11. En cada registro contable, el débito y el crédito deben ser iguales.
12. El valor total del débito (o crédito) contabilizado debe ser igual al total de la factura.
13. Los registros contables con valor en 0 se marcan como inconsistencia, porque no aportan valor y generan ruido en la conciliación.


## Catálogo de causas

| Código | Descripción |
|---|---|
| CAMPO_VACIO | Campo obligatorio vacío |
| ID_DUPLICADO | Id_Factura duplicado en el archivo de facturas |
| TARIFA_IVA_INVALIDA | Tarifa de IVA no válida (permitidas: 0%, 5%, 19%) |
| DIF_IVA | El valor del IVA no coincide con base × tarifa |
| DIF_RETENCION | El valor de la retención no coincide con base × tarifa |
| DIF_TOTAL | El total no coincide con base + IVA − retención |
| SIN_REGISTRO_CONTABLE | La factura no tiene registro contable |
| ESTADO_PENDIENTE | El registro contable no está en estado Contabilizada |
| DEBITO_CREDITO_DIFERENTE | El débito y el crédito del registro no son iguales |
| DIF_VALOR_CONTABLE | El valor contabilizado no coincide con el total de la factura |
| REGISTRO_CONTABLE_EN_CERO | Existe un registro contable con valor en 0 |

**Advertencias** (no cambian el estado de la factura)

| Código | Descripción |
|---|---|
| VARIOS_PERIODOS | Los registros pertenecen a más de un periodo contable |
| REGISTRO_SIN_FACTURA | Registro contable sin factura asociada |