"""API del conciliador de facturas y retenciones."""

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import COLUMNAS_CONTABILIDAD, COLUMNAS_FACTURAS
from app.services.conciliator import CON_INCONSISTENCIA, CORRECTA, conciliar
from app.services.read_csv import ErrorArchivo, leer_csv

app = FastAPI(title="Conciliador de facturas y retenciones")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)
ultimo_resultado: dict | None = None


async def leer_archivo(archivo: UploadFile, nombre: str, columnas: list[str]) -> list[dict]:
    if not archivo.filename or not archivo.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail=f"El archivo de {nombre} debe ser .csv")
    contenido = await archivo.read()
    try:
        return leer_csv(contenido, nombre, columnas)
    except ErrorArchivo as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/api/health")
def health():
    return {"estado": "ok"}


@app.post("/api/conciliar")
async def procesar(
    facturas: UploadFile = File(...),
    contabilidad: UploadFile = File(...),
):
    """Recibe los dos archivos, aplica las reglas y devuelve el resultado completo."""
    global ultimo_resultado
    filas_facturas = await leer_archivo(facturas, "facturas", COLUMNAS_FACTURAS)
    filas_contabilidad = await leer_archivo(contabilidad, "contabilidad", COLUMNAS_CONTABILIDAD)

    ultimo_resultado = conciliar(filas_facturas, filas_contabilidad)
    return ultimo_resultado


@app.get("/api/resultados")
def consultar(estado: str | None = None):
    """Consulta el último resultado. Permite filtrar el detalle por estado."""
    if ultimo_resultado is None:
        raise HTTPException(status_code=404, detail="Aún no se ha procesado ningún archivo.")

    if estado is None:
        return ultimo_resultado

    if estado not in (CORRECTA, CON_INCONSISTENCIA):
        raise HTTPException(
            status_code=400,
            detail=f"Estado no válido. Use '{CORRECTA}' o '{CON_INCONSISTENCIA}'.",
        )

    detalle = [d for d in ultimo_resultado["detalle"] if d["estado"] == estado]
    return {**ultimo_resultado, "detalle": detalle}
