import { Component, computed, input, output, signal } from '@angular/core';
import { EstadoFactura, FacturaResultado } from '../../models/resultado.model';
import { PesosPipe } from '../../pipes/pesos.pipe';

@Component({
  selector: 'app-tabla-resultados',
  imports: [PesosPipe],
  styleUrl: './tabla-resultados.css',
  templateUrl: './tabla-resultados.html',
})
export class TablaResultados {
  /** Facturas a mostrar (ya filtradas por estado desde la API). */
  facturas = input.required<FacturaResultado[]>();
  /** Estado seleccionado actualmente. null = todas. */
  estado = input<EstadoFactura | null>(null);
  /** Indica si se está consultando la API. */
  cargando = input(false);

  /** Se emite cuando el usuario cambia el filtro de estado. */
  cambioEstado = output<EstadoFactura | null>();

  readonly opcionesEstado: { valor: EstadoFactura | null; texto: string }[] = [
    { valor: null, texto: 'Todas' },
    { valor: 'Correcta', texto: 'Correctas' },
    { valor: 'Con inconsistencia', texto: 'Con inconsistencia' },
  ];

  busqueda = signal('');
  causaSeleccionada = signal('');
  filaAbierta = signal<number | null>(null);

  /** Causas presentes en las facturas mostradas, para el selector. */
  causasDisponibles = computed(() => {
    const causas = new Map<string, string>();
    for (const f of this.facturas()) {
      for (const c of f.causas) {
        causas.set(c.codigo, c.descripcion);
      }
    }
    return [...causas.entries()].map(([codigo, descripcion]) => ({ codigo, descripcion }));
  });

  /** Filtros locales: búsqueda por texto y por causa. */
  facturasVisibles = computed(() => {
    const texto = this.busqueda().trim().toLowerCase();
    const causa = this.causaSeleccionada();
    return this.facturas().filter((f) => {
      const coincideTexto = !texto
        || f.id_factura.toLowerCase().includes(texto)
        || f.nit_proveedor.includes(texto)
        || f.concepto.toLowerCase().includes(texto);
      const coincideCausa = !causa || f.causas.some((c) => c.codigo === causa);
      return coincideTexto && coincideCausa;
    });
  });

  seleccionarEstado(estado: EstadoFactura | null) {
    this.causaSeleccionada.set('');
    this.filaAbierta.set(null);
    this.cambioEstado.emit(estado);
  }

  alternarFila(fila: number) {
    this.filaAbierta.set(this.filaAbierta() === fila ? null : fila);
  }

  diferencia(esperado: number | null, reportado: number | null): number | null {
    return esperado === null || reportado === null ? null : reportado - esperado;
  }

  leerTexto(evento: Event): string {
    return (evento.target as HTMLInputElement).value;
  }
}
