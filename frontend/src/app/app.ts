import { Component, inject, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { ArchivosSeleccionados, CargaArchivos } from './components/carga-archivos/carga-archivos';
import { Resumen } from './components/resumen/resumen';
import { TablaResultados } from './components/tabla-resultados/tabla-resultados';
import { EstadoFactura, FacturaResultado, ResultadoConciliacion } from './models/resultado.model';
import { Conciliacion } from './services/conciliacion';

@Component({
  selector: 'app-root',
  imports: [CargaArchivos, Resumen, TablaResultados],
  styleUrl: './app.css',
  templateUrl: './app.html',
})
export class App {
  private conciliacion = inject(Conciliacion);

  resultado = signal<ResultadoConciliacion | null>(null);
  facturas = signal<FacturaResultado[]>([]);
  estadoFiltro = signal<EstadoFactura | null>(null);
  cargando = signal(false);
  consultando = signal(false);
  error = signal<string | null>(null);

  procesar(archivos: ArchivosSeleccionados) {
    this.cargando.set(true);
    this.error.set(null);
    this.resultado.set(null);

    this.conciliacion.conciliar(archivos.facturas, archivos.contabilidad).subscribe({
      next: (respuesta) => {
        this.resultado.set(respuesta);
        this.facturas.set(respuesta.detalle);
        this.estadoFiltro.set(null);
        this.cargando.set(false);
      },
      error: (err: HttpErrorResponse) => {
        this.error.set(this.mensajeError(err));
        this.cargando.set(false);
      },
    });
  }

  /** El filtro por estado se resuelve en el backend con GET /api/resultados. */
  filtrar(estado: EstadoFactura | null) {
    this.estadoFiltro.set(estado);
    this.consultando.set(true);
    this.error.set(null);

    this.conciliacion.consultar(estado ?? undefined).subscribe({
      next: (respuesta) => {
        this.facturas.set(respuesta.detalle);
        this.consultando.set(false);
      },
      error: (err: HttpErrorResponse) => {
        this.error.set(this.mensajeError(err));
        this.consultando.set(false);
      },
    });
  }

  private mensajeError(err: HttpErrorResponse): string {
    // status 0 = el backend no respondió (apagado o bloqueado por CORS)
    if (err.status === 0) {
      return 'No se pudo conectar con el servidor. Verifique que el backend esté en ejecución en el puerto 8000.';
    }
    return err.error?.detail ?? 'Ocurrió un error inesperado al procesar la solicitud.';
  }
}
