import { Component, inject, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Conciliacion, ConteoRespuesta } from './services/conciliacion';

@Component({
  selector: 'app-root',
  styleUrl: './app.css',
  templateUrl: './app.html',
})
export class App {
  private conciliacion = inject(Conciliacion);

  facturas = signal<File | null>(null);
  contabilidad = signal<File | null>(null);
  cargando = signal(false);
  error = signal<string | null>(null);
  resultado = signal<ConteoRespuesta | null>(null);

  seleccionarFacturas(evento: Event) {
    const input = evento.target as HTMLInputElement;
    this.facturas.set(input.files?.[0] ?? null);
  }

  seleccionarContabilidad(evento: Event) {
    const input = evento.target as HTMLInputElement;
    this.contabilidad.set(input.files?.[0] ?? null);
  }

  procesar() {
    const facturas = this.facturas();
    const contabilidad = this.contabilidad();
    if (!facturas || !contabilidad) {
      this.error.set('Debe seleccionar los dos archivos.');
      return;
    }

    this.cargando.set(true);
    this.error.set(null);
    this.resultado.set(null);

    this.conciliacion.conciliar(facturas, contabilidad).subscribe({
      next: (respuesta) => {
        this.resultado.set(respuesta);
        this.cargando.set(false);
      },
      error: (err: HttpErrorResponse) => {
        const mensaje = err.status === 0
          ? 'No se pudo conectar con el servidor. Verifique que el backend esté encendido.'
          : err.error?.detail ?? 'Ocurrió un error al procesar los archivos.';
        this.error.set(mensaje);
        this.cargando.set(false);
      },
    });
  }
}