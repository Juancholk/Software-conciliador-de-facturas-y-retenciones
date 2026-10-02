import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface ConteoRespuesta {
  facturas_leidas: number;
  registros_contables_leidos: number;
}

@Service()
export class Conciliacion {
  private http = inject(HttpClient);
  private api = 'http://localhost:8000/api';

  conciliar(facturas: File, contabilidad: File) {
    const form = new FormData();
    form.append('facturas', facturas);
    form.append('contabilidad', contabilidad);
    return this.http.post<ConteoRespuesta>(`${this.api}/conciliar`, form);
  }
}