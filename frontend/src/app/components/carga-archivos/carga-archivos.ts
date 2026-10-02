import { Component, input, output, signal } from '@angular/core';

export interface ArchivosSeleccionados {
  facturas: File;
  contabilidad: File;
}

@Component({
  selector: 'app-carga-archivos',
  styleUrl: './carga-archivos.css',
  templateUrl: './carga-archivos.html',
})
export class CargaArchivos {
  /** Indica si el padre está procesando (deshabilita el botón). */
  cargando = input(false);

  /** Se emite cuando el usuario pide procesar los dos archivos. */
  procesar = output<ArchivosSeleccionados>();

  facturas = signal<File | null>(null);
  contabilidad = signal<File | null>(null);
  error = signal<string | null>(null);

  seleccionar(evento: Event, tipo: 'facturas' | 'contabilidad') {
    const input = evento.target as HTMLInputElement;
    const archivo = input.files?.[0] ?? null;
    this.error.set(null);

    if (archivo && !archivo.name.toLowerCase().endsWith('.csv')) {
      this.error.set(`El archivo "${archivo.name}" no es un CSV.`);
      input.value = '';
      return;
    }

    if (tipo === 'facturas') {
      this.facturas.set(archivo);
    } else {
      this.contabilidad.set(archivo);
    }
  }

  enviar() {
    const facturas = this.facturas();
    const contabilidad = this.contabilidad();
    if (!facturas || !contabilidad) {
      this.error.set('Debe seleccionar los dos archivos.');
      return;
    }
    this.procesar.emit({ facturas, contabilidad });
  }
}
