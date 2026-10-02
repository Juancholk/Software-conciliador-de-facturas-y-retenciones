import csv
import io
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Conciliador de facturas y retenciones")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

async def leer_csv(archivo: UploadFile, nombre: str) -> list[dict]:
    """Lee un archivo CSV subido y devuelve sus filas como lista de diccionarios."""
    if not archivo.filename or not archivo.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail=f"El archivo de {nombre} debe ser .csv")

    contenido = await archivo.read()
    if not contenido.strip():
        raise HTTPException(status_code=400, detail=f"El archivo de {nombre} está vacío")

    try:
        texto = contenido.decode("utf-8-sig")  # utf-8-sig elimina el BOM si existe
    except UnicodeDecodeError:
        texto = contenido.decode("latin-1")

    return list(csv.DictReader(io.StringIO(texto)))


@app.get("/api/health")
def health():
    return {"estado": "ok"}


@app.post("/api/conciliar")
async def conciliar(
    facturas: UploadFile = File(...),
    contabilidad: UploadFile = File(...),
):
    filas_facturas = await leer_csv(facturas, "facturas")
    filas_contabilidad = await leer_csv(contabilidad, "contabilidad")

    return {
        "facturas_leidas": len(filas_facturas),
        "registros_contables_leidos": len(filas_contabilidad),
    }