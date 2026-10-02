# Conciliador de facturas y retenciones

Prototipo web que cruza el archivo de facturas de proveedores contra los registros contables, valida los cálculos de IVA, retención y total, y clasifica cada factura como **Correcta** o **Con inconsistencia**, indicando la causa y los valores que la originan.

- **Backend:** Python + FastAPI (API REST con las reglas de negocio).
- **Frontend:** Angular (carga de archivos, resumen, tabla con filtros y detalle por factura).

---

## Contenido

1. [Funcionalidades](#funcionalidades)
2. [Estructura del proyecto](#estructura-del-proyecto)
3. [Requisitos](#requisitos)
4. [Instalación y ejecución](#instalación-y-ejecución)
5. [Uso](#uso)
6. [Pruebas automáticas](#pruebas-automáticas)
7. [API](#api)
8. [Supuestos](#supuestos)
9. [Catálogo de causas](#catálogo-de-causas)
10. [Resultados con los archivos de prueba](#resultados-con-los-archivos-de-prueba)
11. [Decisiones técnicas](#decisiones-técnicas)
12. [Limitaciones y funcionalidades no incluidas](#limitaciones-y-funcionalidades-no-incluidas)
13. [Uso de inteligencia artificial](#uso-de-inteligencia-artificial)

---

## Funcionalidades

- Carga de `facturas.csv` y `contabilidad.csv` desde el navegador.
- Validación de estructura: extensión, archivo vacío y columnas obligatorias (indica cuáles faltan).
- Reglas de negocio:
  - IVA esperado = base gravable × tarifa de IVA.
  - Retención esperada = base gravable × tarifa de retención.
  - Total esperado = base gravable + IVA − retención.
  - Facturas duplicadas, facturas sin registro contable y registros contables sin factura.
  - Estado contable, partida doble (débito = crédito) y valor contabilizado contra el total de la factura.
- Clasificación de cada factura con **todas** sus causas, no solo la primera.
- Resumen: registros leídos, facturas únicas, correctas, con inconsistencia, conteo por causa y monto de las diferencias por concepto.
- Tabla con filtro por estado (resuelto en el backend), búsqueda por id/NIT/concepto y filtro por causa.
- Detalle por factura con la trazabilidad del cálculo: valor esperado, reportado y diferencia.
- Mensajes de carga y de error (archivo inválido, columnas faltantes, backend no disponible).

## Estructura del proyecto

```
├── README.md
├── DECLARACION_IA.md
├── data/
│   ├── facturas.csv              ← archivos de prueba entregados
│   └── contabilidad.csv
├── docs/
│   └── presentacion.pdf          ← presentación ejecutiva
├── backend/
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── main.py               ← API (endpoints, CORS, manejo de errores)
│   │   ├── config.py             ← parámetros: tolerancia, tarifas válidas, columnas
│   │   ├── causas.py             ← catálogo de causas y advertencias
│   │   └── services/
│   │       ├── read_csv.py     ← lectura y validación estructural de los CSV
│   │       └── conciliator.py    ← reglas de negocio (este no depende de FAST API para fines prácticos)
│   └── tests/
│       ├── test_conciliador.py   ← una o más pruebas por regla
│       ├── test_read_csv.py
│       └── test_api.py           ← pruebas de la API con los archivos de data/
└── frontend/
    ├── package.json
    ├── public/logos/
    └── src/app/
        ├── app.ts / app.html     ← componente principal: coordina el flujo
        ├── models/               ← interfaces de la respuesta de la API
        ├── services/             ← llamadas HTTP al backend
        ├── pipes/                ← formato de pesos colombianos
        └── components/
            ├── carga-archivos/
            ├── resumen/
            └── tabla-resultados/
```

## Requisitos

| Herramienta | Versión usada | Notas |
|---|---|---|
| Python | 3.14.8 | Compatible con 3.12 o superior |
| Node.js | 24.21.0 | Angular CLI 22 exige v22.22.3+ o v24.15.0+ |
| npm | 12.2.0 | Se instala con Node.js |
| Angular | 22.2 | Se instala con `npm install`, no requiere instalación global |
| FastAPI | 0.142.2 | Ver `backend/requirements.txt` |

Dependencias principales:

- **Backend:** `fastapi`, `uvicorn`, `python-multipart` (necesaria para recibir archivos), `pytest` y `httpx` (pruebas). La lista completa con versiones exactas está en `backend/requirements.txt`.
- **Frontend:** `@angular/*` y `@fontsource/open-sans` (fuente instalada localmente para no depender de internet). La lista completa está en `frontend/package.json`.

No se requieren credenciales, bases de datos ni variables de entorno.

## Instalación y ejecución

Se necesitan **dos terminales**: una para el backend (puerto 8000) y otra para el frontend (puerto 4200).

### 1. Clonar el repositorio

```bash
git clone https://github.com/Juancholk/Software-conciliador-de-facturas-y-retenciones.git
cd Software-conciliador-de-facturas-y-retenciones
```

### 2. Backend (terminal 1)

```bash
cd backend
python -m venv .venv
```

Activar el entorno virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

> En Windows, si PowerShell bloquea la activación, ejecutar una vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Instalar dependencias e iniciar la API:

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

La API queda disponible en `http://localhost:8000`. La documentación interactiva está en `http://localhost:8000/docs`.

### 3. Frontend (terminal 2)

```bash
cd frontend
npm install
npm start
```

La aplicación queda disponible en `http://localhost:4200`.

> `npm start` ejecuta la versión de Angular CLI instalada en el proyecto, por lo que no es necesario instalar Angular de forma global.

## Uso

1. Abrir `http://localhost:4200`.
2. Seleccionar `data/facturas.csv` en *Facturas de proveedores* y `data/contabilidad.csv` en *Registros contables*.
3. Hacer clic en **Conciliar**.
4. Revisar el resumen y la tabla. Los botones *Todas*, *Correctas* y *Con inconsistencia* filtran por estado.
5. Hacer clic en una fila para ver el detalle de sus causas y la trazabilidad del cálculo.

## Pruebas automáticas

Desde `backend/`, con el entorno virtual activo:

```bash
python -m pytest -v
```

Se ejecutan 30 pruebas: reglas de negocio, lectura de archivos y la API completa con los archivos de prueba. Se usa `python -m pytest` para garantizar que corran con el Python del entorno virtual.

## API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/health` | Verifica que la API esté en funcionamiento. |
| POST | `/api/conciliar` | Recibe `facturas` y `contabilidad` (multipart/form-data), aplica las reglas y devuelve el resultado completo. |
| GET | `/api/resultados?estado=` | Consulta el último resultado procesado. `estado` es opcional: `Correcta` o `Con inconsistencia`. |


## Supuestos

**Datos de entrada**

1. Las tarifas vienen en formato decimal (`0.19` = 19%). Si llega un valor mayor que 1 (`19` o `19%`) se interpreta como porcentaje y se divide entre 100.
2. Todos los campos mínimos definidos en el enunciado son obligatorios. Un campo vacío marca la factura como *Con inconsistencia* sin detener el procesamiento del archivo.
3. Los valores numéricos o fechas que no se pueden interpretar (por ejemplo, `abc` en la base gravable) se marcan como formato no válido.
4. Si los registros pertenecen a varios periodos contables, se muestra una advertencia indicando que se está trabajando con más de un periodo. Esto no cambia el estado de las facturas.

**Cálculos**

5. IVA esperado = `base_gravable × tarifa_iva`.
6. Retención esperada = `base_gravable × tarifa_retencion`.
7. Total esperado = `base_gravable + IVA esperado − retención esperada`, comparado contra `total_factura`. Se usan los valores recalculados y no los reportados, para que cada inconsistencia apunte a su causa: si solo el IVA reportado está mal, la factura se marca por IVA y no también por total.
8. Tarifas de IVA válidas: 0%, 5% y 19%.
9. Se acepta una tolerancia de ±1 peso por redondeo (configurable en `backend/app/config.py`).

**Facturas**

10. Si un `id_factura` aparece más de una vez en el archivo de facturas, todas sus ocurrencias se marcan como "Id_Factura duplicado" y se indica en qué otra fila aparece.
11. Como `contabilidad.csv` no incluye NIT, el cruce se hace únicamente por `id_factura`. Por eso, todas las ocurrencias de un id duplicado se cruzan contra los mismos registros contables y pueden presentar causas distintas según si su valor coincide o no con lo contabilizado. En un escenario real la llave debería ser `nit_proveedor + id_factura`, ya que el número de factura es único por emisor.

**Contabilidad**

12. Solo el estado `Contabilizada` es válido. El estado `Pendiente` se marca como inconsistencia.
13. En cada registro contable, el débito y el crédito deben ser iguales.
14. El valor total del débito contabilizado debe ser igual al total de la factura.
15. Los registros contables con valor en 0 se marcan como inconsistencia, porque no aportan valor y generan ruido en la conciliación.
16. La conciliación se hace en ambas direcciones: cada factura debe tener registro contable y cada registro contable debe tener factura. Los registros sin factura se reportan como inconsistencia en una lista aparte, ya que no corresponden a ninguna factura del archivo.

## Catálogo de causas

Causas que marcan la factura como *Con inconsistencia*:

| Código | Descripción |
|---|---|
| CAMPO_VACIO | Campo obligatorio vacío |
| VALOR_INVALIDO | Valor numérico o fecha con formato no válido |
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
| REGISTRO_SIN_FACTURA | Registro contable sin factura que lo soporte |

**Advertencias** (no cambian el estado de la factura):

| Código | Descripción |
|---|---|
| VARIOS_PERIODOS | Los registros pertenecen a más de un periodo contable |

## Resultados con los archivos de prueba

| Indicador | Valor |
|---|---|
| Registros leídos | 50 |
| Facturas únicas | 48 |
| Correctas | 28 |
| Con inconsistencia | 22 |
| Registros contables leídos | 50 |
| Registros contables sin factura | 0 |

Facturas por causa (una factura puede tener varias):

| Causa | Facturas | Casos |
|---|---|---|
| REGISTRO_CONTABLE_EN_CERO | 7 | FAC-0001 a FAC-0006 (FAC-0004 aparece dos veces) |
| ID_DUPLICADO | 4 | FAC-0004 y FAC-0015, dos ocurrencias cada una |
| SIN_REGISTRO_CONTABLE | 4 | FAC-0007, FAC-0021, FAC-0034, FAC-0042 |
| CAMPO_VACIO | 3 | FAC-0013 (NIT), FAC-0029 (concepto), FAC-0042 (fecha) |
| ESTADO_PENDIENTE | 3 | FAC-0011, FAC-0027, FAC-0039 |
| DIF_TOTAL | 3 | FAC-0009, FAC-0023, FAC-0036 |
| DIF_IVA | 2 | FAC-0006, FAC-0018 |
| DIF_VALOR_CONTABLE | 2 | Segundas ocurrencias de FAC-0004 y FAC-0015 |

Estos valores se verifican automáticamente en `tests/test_api.py`.

## Decisiones técnicas

- **Separación de responsabilidades.** `read_csv.py` valida la estructura del archivo, `conciliator.py` aplica las reglas y `main.py` solo expone la API. Las reglas no dependen de FastAPI, lo que permite probarlas de forma aislada.
- **`Decimal` en lugar de `float`.** Evita errores de precisión en los cálculos monetarios.
- **Lectura tolerante.** Se acepta UTF-8 con o sin BOM y Latin-1, separador coma o punto y coma, y encabezados con espacios o mayúsculas.
- **Trazabilidad.** Cada causa incluye código, descripción y detalle con los valores esperado, reportado y diferencia. Cada factura incluye su número de fila en el CSV.
- **Filtro por estado en el backend.** El frontend consulta `GET /api/resultados?estado=` al cambiar el filtro, de modo que la pantalla usa los dos servicios de la API.
- **Frontend por componentes.** `app.ts` coordina el flujo y llama al servicio; los componentes reciben datos con `input()` y notifican eventos con `output()`.

## Limitaciones y funcionalidades no incluidas

- El último resultado se guarda en memoria del servidor: se pierde al reiniciar el backend y no soporta varios usuarios simultáneos.
- CORS está configurado solo para `http://localhost:4200`.
- No se incluyen pruebas automáticas del frontend.
- No se valida la tarifa de retención según el concepto (compras, servicios, arrendamientos, honorarios) ni las bases mínimas en UVT.
- No se calculan ReteIVA ni ReteICA.
- No se valida el formato ni el dígito de verificación del NIT.
- No hay exportación de resultados ni histórico de conciliaciones.

Los logotipos de Bancolombia y Grupo Cibest se usan únicamente con fines de demostración en esta prueba técnica.

## Uso de inteligencia artificial

Ver [DECLARACION_IA.md](DECLARACION_IA.md).