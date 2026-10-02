import { Pipe, PipeTransform } from '@angular/core';

const formato = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
});

/** Muestra un número como pesos colombianos: 1150000 -> $ 1.150.000 */
@Pipe({ name: 'pesos' })
export class PesosPipe implements PipeTransform {
  transform(valor: number | null | undefined): string {
    return valor === null || valor === undefined ? '—' : formato.format(valor);
  }
}
