import { Component, computed, input } from '@angular/core';
import { ResultadoConciliacion } from '../../models/resultado.model';
import { PesosPipe } from '../../pipes/pesos.pipe';

@Component({
  selector: 'app-resumen',
  imports: [PesosPipe],
  styleUrl: './resumen.css',
  templateUrl: './resumen.html',
})
export class Resumen {
  resultado = input.required<ResultadoConciliacion>();

  resumen = computed(() => this.resultado().resumen);

  porcentajeCorrectas = computed(() => {
    const r = this.resumen();
    return r.registros_leidos ? Math.round((r.correctas / r.registros_leidos) * 100) : 0;
  });

  /** Lista de causas con su descripción, ordenada de mayor a menor. */
  causas = computed(() => {
    const descripciones = new Map<string, string>();
    for (const factura of this.resultado().detalle) {
      for (const c of factura.causas) {
        descripciones.set(c.codigo, c.descripcion);
      }
    }
    const conteo = this.resumen().por_causa;
    const maximo = Math.max(...Object.values(conteo), 1);
    return Object.entries(conteo).map(([codigo, cantidad]) => ({
      codigo,
      cantidad,
      descripcion: descripciones.get(codigo) ?? codigo,
      ancho: (cantidad / maximo) * 100,
    }));
  });
}
